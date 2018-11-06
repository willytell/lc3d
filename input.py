#from abc import ABC, abstractmethod

import glob
import os

from plugin import Plugin
from imageFormat import MyNifty

from configuration import Configuration

# class Input(Plugin):
#     def __init__(self, name):
#         super().__init__(name)

class NiftyManagement(Plugin):
    def __init__(self, name, src_image_path, src_mask_path, mask_pattern, dst_image_path, dst_mask_path):     #mask_pattern = '*.nii.gz'
        self.src_image_path = src_image_path
        self.src_mask_path = src_mask_path
        self.mask_pattern = mask_pattern
        self.dst_image_path = dst_image_path
        self.dst_mask_path = dst_mask_path
        self.src_image_list = []
        self.src_mask_list = []
        self.image = None
        self.mask = None
        super().__init__(name)

    def masks2read(self):
        self.src_mask_list = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(self.src_mask_path, self.mask_pattern)))]
        self.index = 0    # index to be used with the self.src_mask_list list to read all the masks.
        return True

    def get_mask_length(self):
        return len(self.src_mask_list)

    # Image filename: LIDC-IDRI-0001_GT1.nii.gz
    # Mask filename:  LIDC-IDRI-0001_GT1_Mask.nii.gz
    def get_image_filename(self, mask_filename):

        if self.mask_pattern == '*.nii.gz':
            name_splitted = mask_filename.split('.')[0].split('_')
            image_filename = name_splitted[0] + '_' + name_splitted[1] + '.nii.gz'
            return image_filename

    # def images2read(self):
    #     self.src_image_list = []
    #
    #     if self.mask_pattern == '*.nii.gz':
    #         for item in self.src_mask_list:
    #             name_splitted = self.src_mask_list[item].split('.')[0].split('_')
    #             fname = name_splitted[0] + '_' + name_splitted[1] + '.nii.gz'
    #             self.src_image_list.append(fname)
    #             print("{} ==> {}".format(item, fname))
    #     else:
    #         print("Error: NiftyManagement, image2read method.")


    def process(self, config, data):
        print("NiftyManagement plugin...")

        if data.get('CT') is not None:  # if already exist
            data.pop('CT')  # remove item
            print("Removing to data: 'CT':[image, mask]")

        if self.index < len(self.src_mask_list):
            self.mask = MyNifty()
            mask_filename = self.src_mask_list[self.index]
            self.mask.read(self.src_mask_path, mask_filename)
            self.mask.image2array()

            self.image = MyNifty()
            image_filename = self.get_image_filename(mask_filename)
            self.image.read(self.src_image_path, image_filename)
            self.image.image2array()

            assert self.image.volume.shape == self.mask.volume.shape, "In NiftyManagement, the volume shapes of the image and mask must have the same dimension."

            data['CT'] = [self.image, self.mask]     # add item
            print("Adding to data: 'CT':[image, mask]")

            self.index += 1  # increment the index for the next item.
            return True

        else:
            print("All the masks and images have been processed.")
            return False




def debug_NiftyManagement():
    config = Configuration("config/conf_extractfeatures.py", "extract features").load()

    data = {}

    myNiftyHandler = NiftyManagement('myNiftyHandler', \
                                     config.src_image_path, \
                                     config.src_mask_path, \
                                     config.mask_pattern, \
                                     config.dst_image_path, \
                                     config.dst_mask_path)
    myNiftyHandler.masks2read()
    myNiftyHandler.process(config, data)


if __name__ == '__main__':
    debug_NiftyManagement()