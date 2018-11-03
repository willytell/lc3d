import SimpleITK as sitk
import numpy as np

from configuration import Configuration
from abc import ABC, abstractmethod
from scipy.ndimage.measurements import label

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

                assert ncomponents == (len(self.vbbox_list)-1), "In VolumeBBox, ncomponents must be equal to the amount of vbbox."

                # Add the new item to data
                data['CT_mask_vbbox'] = self.vbbox_list
                print("Adding to data: 'CT_mask_vbbox':vbbox_list")

        else:
            print('Error: In the VolumeBBox class, process() method do not found CT_mask_labeled key to process.')



class ExpandVBBox(Plugin):
    def __init__(self,name):
        super().__init__(name)

    @abstractmethod
    def expand(self):
        pass


class UniformExpandVBBox(ExpandVBBox):
    def __init__(self, name, backgroun_percentage, groundtruth_percentage, nvoxel):
        self.backgroun_percentage = backgroun_percentage
        self.groundtruth_percentage = groundtruth_percentage
        self.nvoxel = nvoxel
        self.volume = None
        self.mask = None
        self.expanded_vbbox_list = []
        super().__init__(name)


    # self.count = np.zeros(ncomponents+1)
    def count_all_labels(self, volume, ncomponents, count):
        for l in range(0, ncomponents + 1):   # include the label '0' that corresponds to background.
            count[l] = len(np.where(volume == l)[0])

    def check_only_one_label(self, count, label_number):
        assert label_number != 0, "UniformExpandVBBox, for check_only_one_label: lable_number must be different of background."
        if count[label_number] == count[1:].sum():  # background is discarded
            #print("Only label {} present in the volume.".format(label_number))
            return True
        else:
            print("Checking the label {}, more than one label is present in the volume.".format(label_number))
            return False

    # Must be only background and one label present in the volume.
    def get_percentage(self, count, label_number):
        bg_p = (count[0] * 100.0) / count.sum()   # background percentage
        gt_p = (count[label_number] * 100.0) / count.sum()  # groundtruth percentage
        return bg_p, gt_p


    # growth_xyz = np.arange((True, True, True, ..., True), dtype=bool)
    def expand(self, labeled, minimal_bbox, label_number, ncomponents, nvoxel, growth_xyz):
        bbox = minimal_bbox

        lowest_idx_x = 0
        higest_idx_x = labeled.shape[0]

        lowest_idx_y = 0
        higest_idx_y = labeled.shape[1]

        lowest_idx_z = 0
        higest_idx_z = labeled.shape[2]

        # increse in x negative direction
        if growth_xyz[0]:
            if lowest_idx_x <= (bbox[0]-nvoxel):
                count = np.zeros((ncomponents+1), dtype=np.int)
                volume = labeled[bbox[0]-nvoxel:(bbox[1]+1), bbox[2]:(bbox[3]+1), bbox[4]:(bbox[5]+1)]
                self.count_all_labels(volume, ncomponents, count)
                if self.check_only_one_label(count, label_number):
                    bbox[0] = bbox[0] - nvoxel
                else:
                    growth_xyz[0] = False
                del count
            else:
                growth_xyz[0] = False

        # increse in x positive direction
        if growth_xyz[1]:
            if (bbox[1] + nvoxel) < higest_idx_x:
                count = np.zeros((ncomponents + 1), dtype=np.int)
                volume = labeled[bbox[0]:(bbox[1] + nvoxel + 1), bbox[2]:(bbox[3] + 1), bbox[4]:(bbox[5] + 1)]
                self.count_all_labels(volume, ncomponents, count)
                if self.check_only_one_label(count, label_number):
                    bbox[1] = bbox[1] + nvoxel
                else:
                    growth_xyz = False
                del count
            else:
                growth_xyz[1] = False

        # increse in y negative direction
        if growth_xyz[2]:
            if lowest_idx_y <= (bbox[2] - nvoxel):
                count = np.zeros((ncomponents + 1), dtype=np.int)
                volume = labeled[bbox[0]:(bbox[1] + 1), (bbox[2] - nvoxel):(bbox[3] + 1), bbox[4]:(bbox[5] + 1)]
                self.count_all_labels(volume, ncomponents, count)
                if self.check_only_one_label(count, label_number):
                    bbox[2] = bbox[2] - nvoxel
                else:
                    growth_xyz = False
                del count
            else:
                growth_xyz[2] = False

        # increse in y positive direction
        if growth_xyz[3]:
            if (bbox[3] + nvoxel) < higest_idx_y:
                count = np.zeros((ncomponents + 1), dtype=np.int)
                volume = labeled[bbox[0]:(bbox[1] + 1), bbox[2]:(bbox[3] + nvoxel + 1), bbox[4]:(bbox[5] + 1)]
                self.count_all_labels(volume, ncomponents, count)
                if self.check_only_one_label(count, label_number):
                    bbox[3] = bbox[3] + nvoxel
                else:
                    growth_xyz = False
                del count
            else:
                growth_xyz[3] = False


        # increse in z negative direction
        if growth_xyz[4]:
            if lowest_idx_z <= (bbox[4] - nvoxel):
                count = np.zeros((ncomponents + 1), dtype=np.int)
                volume = labeled[bbox[0]:(bbox[1] + 1), bbox[2]:(bbox[3] + 1), (bbox[4] - nvoxel):(bbox[5] + 1)]
                self.count_all_labels(volume, ncomponents, count)
                if self.check_only_one_label(count, label_number):
                    bbox[4] = bbox[4] - nvoxel
                else:
                    growth_xyz = False
                del count
            else:
                growth_xyz[4] = False

        # increse in z positive direction
        if growth_xyz[5]:
            if (bbox[5] + nvoxel) < higest_idx_z:
                count = np.zeros((ncomponents + 1), dtype=np.int)
                volume = labeled[bbox[0]:(bbox[1] + 1), bbox[2]:(bbox[3] + 1), bbox[4]:(bbox[5] + nvoxel + 1)]
                self.count_all_labels(volume, ncomponents, count)
                if self.check_only_one_label(count, label_number):
                    bbox[5] = bbox[5] + nvoxel
                else:
                    growth_xyz = False
                del count
            else:
                growth_xyz[5] = False

        return bbox


    def bg_p_stuff(self, labeled, minimal_vbbox, ncomponents, label_number):
        count = np.zeros((ncomponents + 1), dtype=np.int)
        volume = labeled[minimal_vbbox[0]:minimal_vbbox[1] + 1, \
                 minimal_vbbox[2]:minimal_vbbox[3] + 1, \
                 minimal_vbbox[4]:minimal_vbbox[5] + 1]
        self.count_all_labels(volume, ncomponents, count)
        print("count = {}".format(count))
        bg_p, gt_p = self.get_percentage(count, label_number)
        print("lable_number : {}".format(label_number))
        print("Initial minimum vbbox: bg_p = {:.2f}, gt_p = {:.2f}".format(round(bg_p, 2), round(gt_p, 2)))
        del count

        return bg_p, gt_p

    def process(self, config, data):
        print("UniformExpandVBBox plugin...")

        # if already exist an item, then remove it.
        if data.get('CT_mask_expanded') is not None:
            data.pop('CT_mask_expanded')
            print("Removeing to data: 'CT_mask_expanded':expanded_vbbox_list")

        if ('CT_mask_labeled' in data) and ('CT_mask_vbbox' in data):
            print("CT_mask_labeled and CT_mask_vbbox are present keys in the data dictionary")

            labeled, ncomponents = data['CT_mask_labeled']
            vbbox_list = data['CT_mask_vbbox']

            for label_number, minimal_vbbox in enumerate(vbbox_list):
                if label_number != 0:

                    bg_p, _ = self.bg_p_stuff(labeled, minimal_vbbox, ncomponents, label_number)

                    if bg_p < self.backgroun_percentage:   # if it's necessary to expand the vbbox.
                        stop = False
                        # growth_xyz represents the directions to growth: [x-, x+, y-, y+, z-, z+]
                        growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)
                        tmp_vbbox = minimal_vbbox

                        while not stop:
                            print("    tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
                            tmp_vbbox = self.expand(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)
                            print("NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

                            bg_p, _ = self.bg_p_stuff(labeled, tmp_vbbox, ncomponents, label_number)
                            if self.backgroun_percentage <= bg_p or not np.any(growth_xyz):
                                self.expanded_vbbox_list.append(tmp_vbbox)
                                stop = True
                                print("Expanded vbbox: {}".format(tmp_vbbox))

                            # del count

                        del growth_xyz
                    else:
                        print("Already enough background!")
                else:
                    # We artificially add as first item a None, which corresponds to the background.
                    # This let us to have label '1' in the index 1, label '2' in the index 2, and so on.
                    self.expanded_vbbox_list.append(None)

            # Add the new item to data
            data['CT_mask_expanded'] = self.expanded_vbbox_list
            print("Adding to data: 'CT_mask_expanded':expanded_vbbox_list")




def test():
    u = UniformExpandVBBox('uniform')
    u.expand()
    u.process(None, None)



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

    uexpandVBBox = UniformExpandVBBox('uniformExpandVBBox', 50.0, 50.0, 1)
    uexpandVBBox.process(config, data)


if __name__ == '__main__':
    debug_test()
    #test()

