from abc import ABC, abstractmethod
import SimpleITK as sitk
import os

class ImageFormat(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def read(self, path, filename):
        pass

    @abstractmethod
    def save(self, path, filename):
        pass


class MyNifty(ImageFormat):
    def __init__(self):
        self.origin = None
        self.spacing = None
        self.direction = None
        self.image = None
        self.volume = None
        super().__init__()

    def read(self, path, filename):
        # Reading the mask
        #fname = '/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CTmask_nii/LIDC-IDRI-0001_GT1_Mask.nii.gz'

        self.image = sitk.ReadImage(os.path.join(path, filename))

        return True

    #def save(self, path, filename):


    # CONVERTING from SimpleITK image to Numpy array
    def image2array(self):
        if self.image is not None:
            self.volume = sitk.GetArrayFromImage(self.image)
        else:
            print("Error: In MyNifty class, image2array method, self.image is None and must be an image of type SimpleITK.")

    # CONVERTING from Numpy to SimpleITK image
    def array2image(self):
        if self.volume is not None:
            self.image = sitk.GetImageFromArray(self.volume)
        else:
            print("Error: In MyNifty class, array2image method, self.volume is None and must be an array of type Numpy.")

    def get_properties(self):
        if self.image is not None:
            origin = self.image.GetOrigin()
            spacing = self.image.GetSpacing()
            direction = self.image.GetDirection()
            return {'origin': origin, 'spacing' : spacing, 'direction' : direction }
        else:
            print("Error: In MyNifty class, get_properties method, self.image is None and must be an image of type SimpleITK.")
            return None

    # Remember to to set the image's origin, spacing, and possibly direction cosine matrix.
    # The default values may not match the physical dimensions of your image.
    def set_properties(self, properties):

        if self.image is not None:
            self.image.SetOrigin(properties['origin'])
            self.image.SetSpacing(properties['spacing'])
            self.image.SetDirection(properties['direction'])

