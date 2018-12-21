#from abc import ABC, abstractmethod

import glob
import os

from plugin import Plugin
from imageFormat import NiftiFormat

from configuration import Configuration

# class Input(Plugin):
#     def __init__(self, name):
#         super().__init__(name)

class NiftiManagementPlugin(Plugin):
    def __init__(self, name, input_key, src_image_path, src_mask_path, mask_pattern, dst_image_path, dst_mask_path, internal=1):     #mask_pattern = '*.nii.gz'
        self.src_image_path = src_image_path
        self.src_mask_path = src_mask_path
        self.mask_pattern = mask_pattern
        self.dst_image_path = dst_image_path
        self.dst_mask_path = dst_mask_path
        self.src_image_list = []
        self.src_mask_list = []
        self.image = None
        self.mask = None
        self.internal = internal
        self.mask_filename = ''
        self.image_filename = ''
        self.caseID = -1        # -1 means Not assigned yet
        self.lessionID = -1     # -1 means Not assigned yet
        super().__init__(name, input_key)

    def masks2read(self):
        self.src_mask_list = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(self.src_mask_path, self.mask_pattern)))]
        self.index = 0    # index to be used with the self.src_mask_list list to read all the masks.
        return True

    def get_mask_length(self):
        return len(self.src_mask_list)

    # Depending on the self.internal value it will find the image's filename.
    def get_image_filename(self, mask_filename):

        # To find the ROIs
        if self.internal == 1:  # image and mask to be processed for first time to obtain the ROIs.
            # Image filename: LIDC-IDRI-0001_GT1.nii.gz
            # Mask filename:  LIDC-IDRI-0001_GT1_Mask.nii.gz
            if self.mask_pattern == '*.nii.gz':
                name_splitted = mask_filename.split('.')[0].split('_')
                image_filename = name_splitted[0] + '_' + name_splitted[1] + '.nii.gz'
                return image_filename

        # To extract the features from the ROIs
        elif self.internal == 2:  # for image and mask ready to extract features
            # Image filename: LIDC-IDRI-0001_GT1_1.nii.gz
            # Mask filename:  LIDC-IDRI-0001_GT1_1_Mask.nii.gz
            if self.mask_pattern == '*.nii.gz':
                name_splitted = mask_filename.split('.')[0].split('_')
                image_filename = name_splitted[0] + '_' + name_splitted[1] + '_' + name_splitted[2] + '.nii.gz'

                # Assign the caseID and lessionID
                self.lessionID = name_splitted[2]
                self.caseID = name_splitted[0].split('-')[2]

                return image_filename
        else:
            print("NiftiManagementPlugin: Error, unknown 'internal' pattern of name.")
            return None


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
    #         print("Error: NiftiManagement, image2read method.")


    def process(self,data):
        print("> NiftiManagement plugin with name: {} ...".format(self.name))

        #self.name equal to 'CT'
        if data.get(self.name) is not None:  # if already exist
            data.pop(self.name)  # remove item
            print("    Removing to data: '{}':[image, mask]".format(self.name))

        if self.index < len(self.src_mask_list):
            # read the mask file
            self.mask = NiftiFormat()
            self.mask_filename = self.src_mask_list[self.index]
            self.mask.read(self.src_mask_path, self.mask_filename)
            self.mask.image2array()
            print("    Mask shape:  {}".format(self.mask.volume.shape))

            # read the image file
            self.image = NiftiFormat()
            self.image_filename = self.get_image_filename(self.mask_filename)
            self.image.read(self.src_image_path, self.image_filename)
            self.image.image2array()
            print("    Image shape: {}".format(self.image.volume.shape))

            assert self.image.volume.shape == self.mask.volume.shape, "    In NiftiManagement, it is supposed that image's volume and mask's volume should have the same shape."

            # add item
            data[self.name] = [self.image, self.mask, self.image_filename, self.mask_filename, self.caseID, self.lessionID]
            print("    Adding to data: '{}':[image, mask, image_filename, mask_filename, caseID, lessionID]".format(self.name))

            self.index += 1  # increment the index for the next file to be read.
            return True

        else:
            print("All the masks and images have been processed.")
            return False




def debug_NiftiManagement():
    config = Configuration("config/conf_extractfeatures.py", "extract features").load()

    data = {}

    myNiftiHandler = NiftiManagementPlugin('myNiftiHandler', \
                                           config.src_image_path, \
                                           config.src_mask_path, \
                                           config.mask_pattern, \
                                           config.dst_image_path, \
                                           config.dst_mask_path)
    myNiftiHandler.masks2read()
    myNiftiHandler.process(data)


if __name__ == '__main__':
    debug_NiftiManagement()