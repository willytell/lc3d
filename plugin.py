import SimpleITK as sitk
import numpy as np
import os

from configuration import Configuration
from abc import ABC, abstractmethod
from scipy.ndimage.measurements import label
from imageFormat import MyNifty
from utils import get_dst_filename_nifty
from slidingwindow import SlidingWindow

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
            return True

        else:
            print('Error: In the Labeling, process() method does not found CT key to process.')

        return False



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
                return True

        else:
            print('Error: In the VolumeBBox, process() method does not found CT_mask_labeled key to process.')

        return False



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

        self.expanded_vbbox_list = []

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
            return True
        else:
            print("Error: In ExpandVBBox, process() method does not found CT_mask_labeled and CT_mask_vbbox keys to process.")

        return False


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

            return True

        else:
            print("Error: In SaveVBBoxNifty, process() method does not found CT and CT_mask_expanded keys to process.")

        return False


class SlidingWindowPlugin(Plugin):
    def __init__(self,name, slidingWindow, strategy):
        self.slidingWindow = slidingWindow   # <--- do it inside the processingX
        self.strategy = strategy
        self.image = None
        super().__init__(name)

        # create a mask with the size of the window size with all in 1's <--- do it inside the processingX

    def context_interface(self, array):
        self.strategy.featureExtraction(array)

    def process(self, config, data):
        print("SlidingWindow plugin...")

        if 'CT' in data:
            print("CT is a present key in the data dictionary")
            self.image, _ = data['CT']  # remember that self.image is a MyNifty object.

            # adding Pad to the volume
            self.image.volume = self.slidingWindow.padding(self.image.volume)

            # mini_cubes will contains all the volumes generated after slide the window throughout the volume.
            # By the way, mini_cubes is an numpy object.
            mini_cubes = self.slidingWindow.rolling_window(self.image.volume)

            # extract features and save them.
            self.strategy.featureExtraction(mini_cubes)

            return True

        else:
            print('Error: In the SlidingWindowPlugin, process() method does not found CT key to process.')

        return False




def debug_test():
    from utils import get_components
    from input import NiftyManagement
    from expansionStrategy import UniformExpansion

    config = Configuration("config/conf_extractfeatures.py", "extract features").load()

    data = {}

    # Plugin NiftyManagement
    myNiftyHandler = NiftyManagement('myNiftyHandler',
                                     config.src_image_path,
                                     config.src_mask_path,
                                     config.mask_pattern,
                                     config.dst_image_path,
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

