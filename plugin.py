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
    def process(self, config, data):
        print ("Labeling plugin...")
        if 'CT_mask' in data:
            print("CT_mask is a key in the data dictionary")
            _, volume = data['CT_mask']

            structure_element = np.ones((3, 3, 3), dtype=np.int)
            labeled, ncomponents = label(volume, structure_element)

            if 'CT_mask_labeled' not in data:
                data['CT_mask_labeled'] = [labeled, ncomponents]
                print("new labeled item added...")
                print("Labeling done!!")

        else:
            print('nothing...')




def test():
    print("Testing plugin...")

    config = Configuration("config/conf_extractfeatures.py", "extract features")

    # Reading the mask
    fname = '/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CTmask_nii/LIDC-IDRI-0001_GT1_Mask.nii.gz'
    img = sitk.ReadImage(fname)

    # CONVERTING from SimpleITK image to Numpy array
    mask = sitk.GetArrayFromImage(img)

    data_map = {'CT_mask':[img, mask]}
    l = Labeling('labeling')
    l.process(config, data_map)


if __name__ == '__main__':
    test()

