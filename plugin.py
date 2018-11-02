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
        if 'CT' in data:
            print("CT is a present key in the data dictionary")
            _, self.mask = data['CT']


            self.labeled, self.ncomponents = label(self.mask.volume, self.structure_element)
            print("Labeling labeled ncomponents: {}".format(self.ncomponents))


            if data.get('CT_mask_labeled') is not None:  # if already exist
                data.pop(self.name)  # remove item

            data['CT_mask_labeled'] = [self.labeled, self.ncomponents]  # add item
            print("Adding to data: 'CT_mask_labeled':[labeled, ncomponents]")

        else:
            print('Error: In the Labeling class, process() method do not found CT key to process.')




class VolumeBBox(Plugin):
    def __init__(self, name):
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

    def expand_in_x(self, labeled, vbbox, decrease_nvoxels, increment_nvoxels):
        dim = labeled.shape[0]






    def process(self, config, data):
        print("VolumeBBox plugin...")
        if 'CT_mask_labeled' in data:
            print("CT_mask_labeled is a present key in the data dictionary")
            labeled, ncomponents = data['CT_mask_labeled']

            # If there is one or more components
            if ncomponents > 0:
                for i in range(1, ncomponents+1):    # from 1 to (ncomponents+1), with ncomoponents equal to 2 ==> 1,2
                    mask = np.zeros(labeled.shape, dtype=np.int)
                    mask[np.where(labeled==i)]=1

                    vbbox = self.bbox_3D(mask)
                    print("vbbox(xmin, xmax, ymin, ymax, zmin, zmax): {}".format(vbbox))

                    # EXACT ROI
                    # volume_bbox = labeled[vbbox[0]:(vbbox[1]+1), vbbox[2]:(vbbox[3]+1), vbbox[4]:(vbbox[5]+1)]

                    # ROI with 1 extra voxel
                    #volume_bbox = labeled[vbbox[0] - 1:(vbbox[1] + 2), vbbox[2] - 1:(vbbox[3] + 2), vbbox[4] - 1:(vbbox[5] + 2)]

                    del mask









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


if __name__ == '__main__':
    debug_test()

