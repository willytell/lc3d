import SimpleITK as sitk
import numpy as np
import os

from configuration import Configuration
from abc import ABC, abstractmethod
from scipy.ndimage.measurements import label
from imageFormat import MyNifty
from utils import get_dst_filename_nifty

class Plugin(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

    @abstractmethod
    def process(self, config, data):
        pass


class Labeling(Plugin):
    def __init__(self, name):
        self.structure_element = None
        self.ncomponents = None
        self.labeled = None
        super().__init__(name)

    def set_structure_element(self, dim_x, dim_y, dim_z):
        self.structure_element = np.ones((dim_x, dim_y, dim_z), dtype=np.int)

    def get_structure_element(self):
        return self.structure_element


    def process(self, config, data):
        print ("Labeling plugin...")

        # if already exist an item, then remove it.
        if data.get('CT_mask_labeled') is not None:
            data.pop('CT_mask_labeled')
            print("Removing to data: 'CT_mask_labeled':[labeled, ncomponents]")

        if 'CT' in data:
            print("CT is a present key in the data dictionary")
            _, self.mask = data['CT']

            self.labeled, self.ncomponents = label(self.mask.volume, self.structure_element)
            print("Labeling labeled ncomponents: {}".format(self.ncomponents))

            # Add the new item to data
            data['CT_mask_labeled'] = [self.labeled, self.ncomponents]
            print("Adding to data: 'CT_mask_labeled':[labeled, ncomponents]")

        else:
            print('Error: In the Labeling class, process() method do not found CT key to process.')



class VolumeBBox(Plugin):
    def __init__(self, name):
        self.vbbox_list = []
        super().__init__(name)

    # Input:  volume (is a mask) where 0 means background and 1 means groundtruth
    # Output: Volume Bounding Box for the volumen: xmin, xma, ymin, ymax, zmin, zmax
    def bbox_3D(self, volume):

        r = np.any(volume, axis=(1, 2))
        c = np.any(volume, axis=(0, 2))
        z = np.any(volume, axis=(0, 1))

        rmin, rmax = np.where(r)[0][[0, -1]]
        cmin, cmax = np.where(c)[0][[0, -1]]
        zmin, zmax = np.where(z)[0][[0, -1]]

        return [rmin, rmax, cmin, cmax, zmin, zmax]

    def process(self, config, data):
        print("VolumeBBox plugin...")

        # if already exist an item, then remove it.
        if data.get('CT_mask_vbbox') is not None:
            data.pop('CT_mask_vbbox')
            print("Removeing to data: 'CT_mask_vbbox':vbbox_list")

        if 'CT_mask_labeled' in data:
            print("CT_mask_labeled is a present key in the data dictionary")
            labeled, ncomponents = data['CT_mask_labeled']

            self.vbbox_list = []

            # If there is one or more components
            if ncomponents > 0:

                # We artificially add as first item a None, which corresponds to the background.
                # This let us to have label '1' in the index 1, label '2' in the index 2, and so on.
                self.vbbox_list.append(None)

                for i in range(1, ncomponents+1):    # from 1 to (ncomponents+1), with ncomoponents equal to 2 ==> 1,2.
                    mask = np.zeros(labeled.shape, dtype=np.int)
                    mask[np.where(labeled==i)]=1

                    vbbox = self.bbox_3D(mask)   # Find the exact position for the volume bounding box
                    print("For the label {} its volume bbox is (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(i, vbbox))

                    self.vbbox_list.append(vbbox)
                    del mask

                # ncomponents does not have included the background.
                assert (ncomponents + 1) == len(self.vbbox_list), "In VolumeBBox, ncomponents must be equal to the amount of vbbox."

                # Add the new item to data
                data['CT_mask_vbbox'] = self.vbbox_list
                print("Adding to data: 'CT_mask_vbbox':vbbox_list")

        else:
            print('Error: In the VolumeBBox class, process() method do not found CT_mask_labeled key to process.')



class ExpandVBBox(Plugin):
    def __init__(self,name, strategy):
        self.strategy = strategy
        self.expanded_vbbox_list = []
        super().__init__(name)

    def context_interface(self, labeled, minimal_vbbox, ncomponents, label_number):
        vbbox = self.strategy.expand(labeled, minimal_vbbox, ncomponents, label_number)
        return vbbox

    def process(self, config, data):
        print("UniformExpandVBBox plugin...")

        # if already exist an item, then remove it.
        if data.get('CT_mask_expanded') is not None:
            data.pop('CT_mask_expanded')
            print("Removeing to data: 'CT_mask_expanded':expanded_vbbox_list")

        # Get some items from data dictionary
        if ('CT_mask_labeled' in data) and ('CT_mask_vbbox' in data):
            print("CT_mask_labeled and CT_mask_vbbox are present keys in the data dictionary")

            labeled, ncomponents = data['CT_mask_labeled']
            vbbox_list = data['CT_mask_vbbox']  # list with minimals vbbox.

            for label_number, minimal_vbbox in enumerate(vbbox_list):
                if label_number != 0:
                    vbbox = self.context_interface(labeled, minimal_vbbox, ncomponents, label_number)
                    self.expanded_vbbox_list.append(vbbox)
                else:
                    # We artificially add as first item a None, which corresponds to the background.
                    # This let us to have label '1' in the index 1, label '2' in the index 2, and so on.
                    self.expanded_vbbox_list.append(None)

            # ncomponents does not have included the background.
            assert (ncomponents+1)== len(self.expanded_vbbox_list), "ExpandVBBox, ncomponents must be equal to the amount of vbbox."

            # Add the new item to data
            data['CT_mask_expanded'] = self.expanded_vbbox_list
            print("Adding to data: 'CT_mask_expanded':expanded_vbbox_list")


class ExpansionStrategy(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

        @abstractmethod
        def expand(self):
            pass


class UniformExpansion(ExpansionStrategy):
    def __init__(self, name, background_percentage, groundtruth_percentage, nvoxel, check_bg_percentage):
        self.background_percentage = background_percentage
        self.groundtruth_percentage = groundtruth_percentage
        self.nvoxel = nvoxel
        self.check_bg_percentage = check_bg_percentage
        self.expanded_vbbox_list = []
        super().__init__(name)

    #count = np.zeros(ncomponents + 1)
    def count_all_labels(self, volume, ncomponents, count):
        for l in range(0, ncomponents + 1):   # include the label '0' that corresponds to background.
            count[l] = len(np.where(volume == l)[0])

    def one_label_present(self, count, label_number):
        assert label_number != 0, "UniformExpand, one_label does not verify one label for background."
        if count[label_number] == count[1:].sum():  # background is discarded
            #print("The label {} is the only one present in the volume.".format(label_number))
            return True
        else:
            #print("The label {} is not the only one present in the volume.".format(label_number))
            return False

    # Must be only background and one label present in the volume.
    def percentage_calculation(self, count, label_number):
        bg_p = (count[0] * 100.0) / count.sum()   # background percentage
        gt_p = (count[label_number] * 100.0) / count.sum()  # groundtruth percentage
        return bg_p, gt_p

    def get_percentage(self, labeled, vbbox, ncomponents, label_number):
        count = np.zeros((ncomponents + 1), dtype=np.int)
        volume = labeled[vbbox[0]:vbbox[1] + 1, \
                         vbbox[2]:vbbox[3] + 1, \
                         vbbox[4]:vbbox[5] + 1]
        self.count_all_labels(volume, ncomponents, count)
        print("label_number : {}".format(label_number))
        print("count = {}".format(count))
        bg_p, gt_p = self.percentage_calculation(count, label_number)
        print("Percentage of vbbox: bg_p = {:.2f}, gt_p = {:.2f}".format(round(bg_p, 2), round(gt_p, 2)))
        del count

        return bg_p, gt_p


    def uniform_expansion(self, labeled, initial_vbbox, label_number, ncomponents, nvoxel, growth_xyz):
        #def expand(self, labeled, minimal_bbox, label_number, ncomponents, nvoxel, growth_xyz):


    #####################################################################################################
    #                                                                                                   #
    #   We define five function, one for each direction in which is posible to increase the vbbox.      #
    #                                                                                                   #
    #   # increse in x negative direction                                                               #
        def zero():
            if growth_xyz[0]:
                if lowest_idx_x <= (vbbox[0] - nvoxel):
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[(vbbox[0]-nvoxel):vbbox[1]+1, vbbox[2]:vbbox[3]+1, vbbox[4]:vbbox[5]+1]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[0] -= nvoxel
                    else:
                        growth_xyz[0] = False
                    del count
                else:
                    growth_xyz[0] = False

        # increse in x positive direction
        def one ():
            if growth_xyz[1]:
                if (vbbox[1] + nvoxel) < higest_idx_x:
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + nvoxel + 1), vbbox[2]:(vbbox[3] + 1), vbbox[4]:(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[1] += nvoxel
                    else:
                        growth_xyz[1] = False
                    del count
                else:
                    growth_xyz[1] = False

        # increse in y negative direction
        def two():
            if growth_xyz[2]:
                if lowest_idx_y <= (vbbox[2] - nvoxel):
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), (vbbox[2] - nvoxel):(vbbox[3] + 1), vbbox[4]:(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[2] -= nvoxel
                    else:
                        growth_xyz[2] = False
                    del count
                else:
                    growth_xyz[2] = False

        # increse in y positive direction
        def three():
            if growth_xyz[3]:
                if (vbbox[3] + nvoxel) < higest_idx_y:
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), vbbox[2]:(vbbox[3] + nvoxel + 1), vbbox[4]:(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[3] += nvoxel
                    else:
                        growth_xyz[3] = False
                    del count
                else:
                    growth_xyz[3] = False


        # increse in z negative direction
        def four():
            if growth_xyz[4]:
                if lowest_idx_z <= (vbbox[4] - nvoxel):
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), vbbox[2]:(vbbox[3] + 1), (vbbox[4] - nvoxel):(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[4] -= nvoxel
                    else:
                        growth_xyz[4] = False
                    del count
                else:
                    growth_xyz[4] = False

        # increse in z positive direction
        def five():
            if growth_xyz[5]:
                if (vbbox[5] + nvoxel) < higest_idx_z:
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), vbbox[2]:(vbbox[3] + 1), vbbox[4]:(vbbox[5] + nvoxel + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[5] += nvoxel
                    else:
                        growth_xyz[5] = False
                    del count
                else:
                    growth_xyz[5] = False


    #                                                                                                   #
    #       End of the five function definition                                                         #
    #                                                                                                   #
    #####################################################################################################



        vbbox = initial_vbbox

        lowest_idx_x = 0
        higest_idx_x = labeled.shape[0]

        lowest_idx_y = 0
        higest_idx_y = labeled.shape[1]

        lowest_idx_z = 0
        higest_idx_z = labeled.shape[2]

        # Defining a dictionary with function to expand the vbbox.
        fc_dict = {0:zero, 1:one, 2:two, 3:three, 4:four, 5:five}

        stop = False
        idx = 0
        while idx < (len(growth_xyz)-1) and (not stop):
            myfunc = fc_dict[idx]
            myfunc()

            if self.check_bg_percentage:
                bg_p, _ = self.get_percentage(labeled, vbbox, ncomponents, label_number)
                if bg_p > self.background_percentage:
                    growth_xyz[0:] = False
                    stop = True

            idx += 1

        return vbbox


    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):

        bg_p, _ = self.get_percentage(labeled, minimal_vbbox, ncomponents, label_number)
        tmp_vbbox = minimal_vbbox

        if bg_p < self.background_percentage:  # if it's necessary to expand the vbbox.
            stop = False
            # growth_xyz represents the directions to growth: [x-, x+, y-, y+, z-, z+]
            growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)

            while not stop:
                print("    tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
                tmp_vbbox = self.uniform_expansion(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)
                print("NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

                bg_p, _ = self.get_percentage(labeled, tmp_vbbox, ncomponents, label_number)
                if self.background_percentage <= bg_p or not np.any(growth_xyz):
                    stop = True

            del growth_xyz
        else:
            print("Already enough background!")


        print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox



class SaveVBBoxNifty(Plugin):
    def __init__(self, name, dst_image_path, dst_mask_path):
        self.dst_image_path = dst_image_path
        self.dst_mask_path = dst_mask_path
        # self.image = None
        # self.mask = None
        super().__init__(name)

    def process(self, config, data):
        print("SaveVBBox plugin...")

        # This plugin does not add any item to 'data', thus it is not necessary to
        # check or remove anything from this plugin in the data dictionary.

        if ('CT' in data) and ('CT_mask_expanded' in data):
            print("CT and CT_mask_expanded are present keys in the data dictionary")

            image, mask = data['CT']
            vbbox_list = data['CT_mask_expanded']

            # check image and mask must be object from MyNifty class.

            for label_number, vbbox in enumerate(vbbox_list):
                if label_number != 0:       # skipping the background, which has a label = 0.

                    # Mask
                    expanded_mask = MyNifty()
                    expanded_mask.volume = np.copy(mask.volume[vbbox[0]:vbbox[1]+1, \
                                                               vbbox[2]:vbbox[3]+1, \
                                                               vbbox[4]:vbbox[5]+1])
                    expanded_mask.array2image()
                    expanded_mask.set_properties(properties=mask.get_properties())
                    # Get the names for the image and mask
                    image_fname, mask_fname = get_dst_filename_nifty(mask.filename, label_number)
                    expanded_mask.save(self.dst_mask_path, mask_fname)

                    # Image
                    expanded_image = MyNifty()
                    expanded_image.volume = np.copy(image.volume[vbbox[0]:vbbox[1]+1, \
                                                                 vbbox[2]:vbbox[3]+1, \
                                                                 vbbox[4]:vbbox[5]+1])
                    expanded_image.array2image()
                    expanded_image.set_properties(properties=image.get_properties())
                    expanded_image.save(self.dst_image_path, image_fname)





def debug_test():
    from utils import get_components
    from input import NiftyManagement

    config = Configuration("config/conf_extractfeatures.py", "extract features").load()

    data = {}

    # Plugin NiftyManagement
    myNiftyHandler = NiftyManagement('myNiftyHandler', \
                                     config.src_image_path, \
                                     config.src_mask_path, \
                                     config.mask_pattern, \
                                     config.dst_image_path, \
                                     config.dst_mask_path)
    myNiftyHandler.masks2read()
    myNiftyHandler.process(config, data)



    # Plugin Labeling
    labeling = Labeling('labeling')
    dim_x, dim_y, dim_z = get_components(config.labeling_se_dim)
    labeling.set_structure_element(dim_x, dim_y, dim_z)
    labeling.process(config, data)

    # Plugin VolumeBBox
    volumeBBox =  VolumeBBox('volumeBBox')
    volumeBBox.process(config, data)

    # Plugin UniformExpandVBBox
    uniformExpansionVBBox = UniformExpansion('uniform', config.background_p, config.groundtruth_p, config.nvoxels, config.check_bg_percentage)
    expandVBBox = ExpandVBBox('expand_vbbox', uniformExpansionVBBox)
    expandVBBox.process(config, data)

    # Plugin SaveVBBoxNifty
    saveVBBoxNifty = SaveVBBoxNifty('SaveVBBoxNifty', config.dst_image_path, config.dst_mask_path)
    saveVBBoxNifty.process(config, data)


if __name__ == '__main__':
    debug_test()
    #test()

