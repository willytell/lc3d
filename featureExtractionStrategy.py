from abc import ABC, abstractmethod
import SimpleITK as sitk
import numpy as np
import six
import radiomics
from radiomics import featureextractor  # This module is used for interaction with pyradiomics


def rolling_window(array, window=(0,), asteps=None, wsteps=None, axes=None, toend=True):

    array = np.asarray(array)
    orig_shape = np.asarray(array.shape)
    window = np.atleast_1d(window).astype(int)  # maybe crude to cast to int...

    if axes is not None:
        axes = np.atleast_1d(axes)
        w = np.zeros(array.ndim, dtype=int)
        for axis, size in zip(axes, window):
            w[axis] = size
        window = w

    # Check if window is legal:
    if window.ndim > 1:
        raise ValueError("`window` must be one-dimensional.")
    if np.any(window < 0):
        raise ValueError("All elements of `window` must be larger then 1.")
    if len(array.shape) < len(window):
        raise ValueError("`window` length must be less or equal `array` dimension.")

    _asteps = np.ones_like(orig_shape)
    if asteps is not None:
        asteps = np.atleast_1d(asteps)
        if asteps.ndim != 1:
            raise ValueError("`asteps` must be either a scalar or one dimensional.")
        if len(asteps) > array.ndim:
            raise ValueError("`asteps` cannot be longer then the `array` dimension.")
        # does not enforce alignment, so that steps can be same as window too.
        _asteps[-len(asteps):] = asteps

        if np.any(asteps < 1):
            raise ValueError("All elements of `asteps` must be larger then 1.")
    asteps = _asteps

    _wsteps = np.ones_like(window)
    if wsteps is not None:
        wsteps = np.atleast_1d(wsteps)
        if wsteps.shape != window.shape:
            raise ValueError("`wsteps` must have the same shape as `window`.")
        if np.any(wsteps < 0):
            raise ValueError("All elements of `wsteps` must be larger then 0.")

        _wsteps[:] = wsteps
        _wsteps[window == 0] = 1  # make sure that steps are 1 for non-existing dims.
    wsteps = _wsteps

    # Check that the window would not be larger then the original:
    if np.any(orig_shape[-len(window):] < window * wsteps):
        raise ValueError("`window` * `wsteps` larger then `array` in at least one dimension.")

    new_shape = orig_shape  # just renaming...

    # For calculating the new shape 0s must act like 1s:
    _window = window.copy()
    _window[_window == 0] = 1

    new_shape[-len(window):] += wsteps - _window * wsteps
    new_shape = (new_shape + asteps - 1) // asteps
    # make sure the new_shape is at least 1 in any "old" dimension (ie. steps
    # is (too) large, but we do not care.
    new_shape[new_shape < 1] = 1
    shape = new_shape

    strides = np.asarray(array.strides)
    strides *= asteps
    new_strides = array.strides[-len(window):] * wsteps

    # The full new shape and strides:
    if toend:
        new_shape = np.concatenate((shape, window))
        new_strides = np.concatenate((strides, new_strides))
    else:
        _ = np.zeros_like(shape)
        _[-len(window):] = window
        _window = _.copy()
        _[-len(window):] = new_strides
        _new_strides = _

        new_shape = np.zeros(len(shape) * 2, dtype=int)
        new_strides = np.zeros(len(shape) * 2, dtype=int)

        new_shape[::2] = shape
        new_strides[::2] = strides
        new_shape[1::2] = _window
        new_strides[1::2] = _new_strides

    new_strides = new_strides[new_shape != 0]
    new_shape = new_shape[new_shape != 0]

    return np.lib.stride_tricks.as_strided(array, shape=new_shape, strides=new_strides)

# Abstract class
class FeatureExtractionStrategy(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

    @abstractmethod
    def featureExtraction(self, array):
        pass


class MyRadiomic(FeatureExtractionStrategy):
    def __init__(self, name):
        self.maskITK = None
        self.extractor = None
        super().__init__(name)

    def build_mask_trick(self, window_size):
        # build a 3D mask with all in 1's, then it is converted to SimpleITK.
        mask = np.ones((window_size, window_size, window_size), dtype=np.int)
        self.maskITK = sitk.GetImageFromArray(mask)

    def build_extractor(self, paramPath):
        # Instantiate the extractor with the parameters in the file paramPath.
        self.extractor = featureextractor.RadiomicsFeaturesExtractor(paramPath)

        print("Using configuration file to parameters: {}".format(paramPath))
        print('Extraction parameters:\n\t', self.extractor.settings)
        print('Enabled filters:\n\t', self.extractor._enabledImagetypes)
        print('Enabled features:\n\t', self.extractor._enabledFeatures)


    def featureExtraction(self, array):
        print("Using Radiomic to extract features...")

        assert type(array).__module__ == np.__name__, "Error, expected a numpy object."
        assert array.ndim == 6, "Error, the array's dimension must be equal to 6."

        max_i, max_j, max_k = array.shape[:3]

        for i in range(max_i):
            for j in range(max_j):
                for k in range(max_k):
                    volume = array[i, j, k]
                    imageITK = sitk.GetImageFromArray(volume)
                    featureVector = self.extractor.execute(imageITK, self.maskITK)   # allways is used the same mask
                    print("-----------------------------------------")
                    print('Result type:', type(featureVector))  # result is returned in a Python ordered dictionary)
                    print('')
                    print('Calculated features')

                    # Show output
                    for featureName in featureVector.keys():
                        #print('Computed %s: %s' % (featureName, featureVector[featureName]))
                        print(featureVector[featureName])

                    #for key, value in six.iteritems(featureVector):
                    #    print('\t', key, ':', value)






def debug_test():
    vol = np.arange(216).reshape(6, 6, 6)
    # rw = rolling_window(a, (3,3,3), asteps=(1,1,2))
    rw = rolling_window(vol, (3, 3, 3), asteps=(1, 1, 1))
    #print(rw)
    print(rw.shape)

    mr = MyRadiomic('myRadiomic')
    mr.build_mask_trick(window_size=3)
    mr.build_extractor(paramPath='/home/willytell/Documentos/PhD/pyradiomics/examples/exampleSettings/Params.yaml')
    mr.featureExtraction(rw)


if __name__ == '__main__':
    debug_test()
    #test()





