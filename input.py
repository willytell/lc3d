#from abc import ABC, abstractmethod

import glob
import os

from plugin import Plugin
from imageFormat import NiftiFormat
import scipy.io as sio
import numpy as np

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
            print("    Removing from data: '{}':[image, mask]".format(self.name))

        if self.index < len(self.src_mask_list):
            # read the mask file
            self.mask = NiftiFormat()
            self.mask_filename = self.src_mask_list[self.index]
            self.mask.read(self.src_mask_path, self.mask_filename)
            self.mask.caseID = self.caseID
            self.mask.lessionID = self.lessionID
            self.mask.image2array(normalize_flag=False)
            print("    Mask shape:  {}".format(self.mask.volume.shape))

            # read the image file
            self.image = NiftiFormat()
            self.image_filename = self.get_image_filename(self.mask_filename)
            self.image.read(self.src_image_path, self.image_filename)
            self.image.caseID = self.caseID
            self.image.lessionID = self.lessionID
            self.image.image2array(normalize_flag=True)
            print("    Image shape: {}".format(self.image.volume.shape))

            assert self.image.volume.shape == self.mask.volume.shape, "    In NiftiManagement, it is supposed that image's volume and mask's volume should have the same shape."

            # add item
            data[self.name] = [self.image, self.mask]
            print("    Adding to data: '{}':[image, mask]".format(self.name))

            self.index += 1  # increment the index for the next file to be read.
            return True

        else:
            print("    All the masks and images have been processed.")
            return False





class MatlabMaskManagementPlugin(Plugin):
    def __init__(self, name, input_key, src_mask_path, mask_pattern, dst_mask_path, variable_name):     #mask_pattern = '*.nii.gz'
        self.src_mask_path = src_mask_path
        self.mask_pattern = mask_pattern
        self.dst_mask_path = dst_mask_path
        self.variable_name = variable_name    # variable_name = 'LungMaskROI'

        self.image = None
        self.mask = None

        self.src_mask_list = []
        self.basename = ''     # e.g.: for the mask file LIDC-IDRI-0005.mat -> the basename is 'LIDC-IDRI-0005'.
        self.filename = ''
        self.numpy_array = None

        super().__init__(name, input_key)

    def masks2read(self):
        self.src_mask_list = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(self.src_mask_path, self.mask_pattern)))]
        self.index = 0    # index to be used with the self.src_mask_list list to read all the masks.
        return True

    def get_mask_list_length(self):
        return len(self.src_mask_list)


    def process(self,data):
        print("> Matlab Mask Management plugin with name: {} ...".format(self.name))

        #self.name equal to 'CT'
        if data.get(self.name) is not None:  # if already exist
            data.pop(self.name)  # remove item
            print("    Removing from data: '{}':[image, mask]".format(self.name))

        if self.index < len(self.src_mask_list):
            # read the mask file
            self.mask = NiftiFormat()
            filename= self.src_mask_list[self.index]
            basename = filename.split('.')[0]
            self.mask.filename = basename
            self.mask.caseID = -1
            self.mask.lessionID = -1

            # Simulating a .nii.gz file and convertion to numpy array.
            matlab_object = sio.loadmat(os.path.join(self.src_mask_path, basename))
            array_xyz = matlab_object[self.variable_name]
            new_array_zyx = np.transpose(array_xyz, (2, 1, 0))
            self.mask.volume = new_array_zyx
            print("    Mask shape:  {}".format(self.mask.volume.shape))

            # Set manually this values
            self.mask.origin = (-1.0, -1.0, 1.0)
            self.mask.spacing = (1.0, 1.0, 1.0)
            self.mask.direction = (-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0)


            # read the image file
            self.image = NiftiFormat()
            self.image.filename = ''
            self.image.caseID = -1
            self.image.lessionID = -1

            # Simulating a .nii.gz file and convertion to numpy array.
            self.image.volume = None #new_array_zyx
            #print("    Image shape: {}".format(self.image.volume.shape))

            #assert self.image.volume.shape == self.mask.volume.shape, \
            #    "    In NiftiManagement, image's volume and mask's volume must have the same shape."

            # add item
            data[self.name] = [self.image, self.mask]
            print("    Adding to data: '{}':[image, mask]".format(self.name))

            self.index += 1  # increment the index for the next file to be read.
            return True

        else:
            print("    All the masks have been processed.")
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