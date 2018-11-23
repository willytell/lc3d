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


class NiftyFormat(ImageFormat):
    def __init__(self):
        self.origin = None
        self.spacing = None
        self.direction = None
        self.image = None
        self.volume = None
        self.path = None
        self.filename = None
        super().__init__()

    def read(self, path, filename):
        self.path = path
        self.filename = filename

        self.image = sitk.ReadImage(os.path.join(self.path, self.filename))
        print("MyNifty, reading: {}".format(os.path.join(self.path, self.filename)))

        # Record properties
        self.origin = self.image.GetOrigin()
        self.spacing = self.image.GetSpacing()
        self.direction = self.image.GetDirection()

    def save(self, path, filename):
        sitk.WriteImage(self.image, os.path.join(path, filename))
        print("MyNifty, writing: {}".format(os.path.join(path, filename)))


    # CONVERTING from SimpleITK image to Numpy array
    def image2array(self):
        if self.image is not None:
            self.volume = sitk.GetArrayFromImage(self.image)
        else:
            print("Error: In MyNifty class, image2array method.")

    # CONVERTING from Numpy to SimpleITK image
    def array2image(self):
        if self.volume is not None:
            self.image = sitk.GetImageFromArray(self.volume)
        else:
            print("Error: In MyNifty class, array2image method.")

    def get_properties(self):
        return {'origin': self.origin, 'spacing' : self.spacing, 'direction' : self.direction }


    # Remember to to set the image's origin, spacing, and possibly direction cosine matrix.
    # The default values may not match the physical dimensions of your image.
    def set_properties(self, properties):
        self.image.SetOrigin(properties['origin'])
        self.image.SetSpacing(properties['spacing'])
        self.image.SetDirection(properties['direction'])

