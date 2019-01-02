from abc import ABC, abstractmethod
import SimpleITK as sitk
import numpy as np
import pandas as pd
import time
import multiprocessing as mp

import os
from collections import OrderedDict
import six
import radiomics
from radiomics import featureextractor  # This module is used for interaction with pyradiomics


# def rolling_window(array, window=(0,), asteps=None, wsteps=None, axes=None, toend=True):
#
#     array = np.asarray(array)
#     orig_shape = np.asarray(array.shape)
#     window = np.atleast_1d(window).astype(int)  # maybe crude to cast to int...
#
#     if axes is not None:
#         axes = np.atleast_1d(axes)
#         w = np.zeros(array.ndim, dtype=int)
#         for axis, size in zip(axes, window):
#             w[axis] = size
#         window = w
#
#     # Check if window is legal:
#     if window.ndim > 1:
#         raise ValueError("`window` must be one-dimensional.")
#     if np.any(window < 0):
#         raise ValueError("All elements of `window` must be larger then 1.")
#     if len(array.shape) < len(window):
#         raise ValueError("`window` length must be less or equal `array` dimension.")
#
#     _asteps = np.ones_like(orig_shape)
#     if asteps is not None:
#         asteps = np.atleast_1d(asteps)
#         if asteps.ndim != 1:
#             raise ValueError("`asteps` must be either a scalar or one dimensional.")
#         if len(asteps) > array.ndim:
#             raise ValueError("`asteps` cannot be longer then the `array` dimension.")
#         # does not enforce alignment, so that steps can be same as window too.
#         _asteps[-len(asteps):] = asteps
#
#         if np.any(asteps < 1):
#             raise ValueError("All elements of `asteps` must be larger then 1.")
#     asteps = _asteps
#
#     _wsteps = np.ones_like(window)
#     if wsteps is not None:
#         wsteps = np.atleast_1d(wsteps)
#         if wsteps.shape != window.shape:
#             raise ValueError("`wsteps` must have the same shape as `window`.")
#         if np.any(wsteps < 0):
#             raise ValueError("All elements of `wsteps` must be larger then 0.")
#
#         _wsteps[:] = wsteps
#         _wsteps[window == 0] = 1  # make sure that steps are 1 for non-existing dims.
#     wsteps = _wsteps
#
#     # Check that the window would not be larger then the original:
#     if np.any(orig_shape[-len(window):] < window * wsteps):
#         raise ValueError("`window` * `wsteps` larger then `array` in at least one dimension.")
#
#     new_shape = orig_shape  # just renaming...
#
#     # For calculating the new shape 0s must act like 1s:
#     _window = window.copy()
#     _window[_window == 0] = 1
#
#     new_shape[-len(window):] += wsteps - _window * wsteps
#     new_shape = (new_shape + asteps - 1) // asteps
#     # make sure the new_shape is at least 1 in any "old" dimension (ie. steps
#     # is (too) large, but we do not care.
#     new_shape[new_shape < 1] = 1
#     shape = new_shape
#
#     strides = np.asarray(array.strides)
#     strides *= asteps
#     new_strides = array.strides[-len(window):] * wsteps
#
#     # The full new shape and strides:
#     if toend:
#         new_shape = np.concatenate((shape, window))
#         new_strides = np.concatenate((strides, new_strides))
#     else:
#         _ = np.zeros_like(shape)
#         _[-len(window):] = window
#         _window = _.copy()
#         _[-len(window):] = new_strides
#         _new_strides = _
#
#         new_shape = np.zeros(len(shape) * 2, dtype=int)
#         new_strides = np.zeros(len(shape) * 2, dtype=int)
#
#         new_shape[::2] = shape
#         new_strides[::2] = strides
#         new_shape[1::2] = _window
#         new_strides[1::2] = _new_strides
#
#     new_strides = new_strides[new_shape != 0]
#     new_shape = new_shape[new_shape != 0]
#
#     return np.lib.stride_tricks.as_strided(array, shape=new_shape, strides=new_strides)

# Abstract class
class FeatureExtractionStrategy(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

    @abstractmethod
    def featureExtraction(self, array):
        pass


class RadiomicClass(FeatureExtractionStrategy):
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
        print("Extraction parameters: {}".format(OrderedDict(sorted(self.extractor.settings.items()))))
        print('Enabled filters:\n\t', OrderedDict(sorted(self.extractor._enabledImagetypes.items())))
        print('Enabled features:\n\t', OrderedDict(sorted(self.extractor._enabledFeatures.items())))

    def featureExtraction(self, array, mask, image_filename, mask_filename, caseID, lessionID, origin, spacing, direction):
        print("      Using Radiomic to extract features...")

        assert type(array).__module__ == np.__name__, "Error, expected a numpy object."
        assert array.ndim == 6, "Error, the array's dimension must be equal to 6."

        max_z, max_x, max_y = array.shape[:3]

        print("         max_z: {}, max_x: {}, max_y: {}".format(max_z, max_x, max_y))
        print("         Extracting new {} rows of features.".format(max_z * max_x * max_y))

        start_time = time.process_time()

        mydict = []
        for x in range(max_x):  # x: row
            for y in range(max_y):  # y: column
                for z in range(max_z):  # z: deep

                    volume = array[z, x, y]     # get a cube from the array.
                    imageITK = sitk.GetImageFromArray(volume)

                    imageITK.origin = origin
                    imageITK.spacing = spacing
                    imageITK.direction = direction

                    new_row = {}

                    featureVector = self.extractor.execute(imageITK, self.maskITK)  # allways is used the same mask
                    # print("Result type: {} and length: {}".format(type(featureVector), len(featureVector)))  # result is returned in a Python ordered dictionary)
                    # print('')
                    # print('Calculated features')
                    for featureName in featureVector.keys():  # Note that featureVectors is a 'disordered dictionary'
                        # print('Computed %s: %s' % (featureName, featureVector[featureName]))
                        # print(featureVector[featureName])
                        if ('firstorder' in featureName) or ('glszm' in featureName) or \
                            ('glcm' in featureName) or ('glrlm' in featureName) or \
                            ('gldm' in featureName):
                            new_row.update({featureName: featureVector[featureName]})

                    lst = sorted(new_row.items()) # Ordering the new_row dictionary

                    # Adding some columns and values at the front of the list
                    label_value = mask[z, x, y]
                    lst.insert(0, ('label', label_value))
                    lst.insert(0, ('axisZ', z))
                    lst.insert(0, ('axisY', y))
                    lst.insert(0, ('axisX', x))
                    # flattened_index = np.ravel_multi_index([[z], [y], [x]], (3, 3, 3), order='F')
                    #                 np.ravel_multi_index([[2],[1],[0]],rw.shape[:3])
                    [flattened_index] = np.ravel_multi_index([[x], [y], [z]], (max_x, max_y, max_z))  # order='C'
                    lst.insert(0, ('flattened_index', int(flattened_index)))
                    lst.insert(0, ('lessionID', lessionID))
                    lst.insert(0, ('caseID', caseID))
                    lst.insert(0, ('mask_filename', mask_filename))
                    lst.insert(0, ('image_filename', image_filename))


                    od = OrderedDict(lst)
                    # for name in od.keys():
                    #     print('Computed %s: %s' % (name, od[name]))


                    mydict.append(od)

        df = pd.DataFrame.from_dict(mydict)

        elapsed_time = time.process_time() - start_time  # it measures in seconds
        print("      Elapsed time for Radiomic to extract features: {:.2f} seconds.".format(elapsed_time))

        return df



############################ PARALLEL COMPUTING ######################################################

results = []

def collect_result(result):
    global results
    results.append(result)

def do_it(i, x, y, z, flattened_index, winSize, paramPath, volume, label_value, image_filename, mask_filename, caseID, lessionID, origin, spacing, direction):

    #print("Process {} working in index: {}".format(os.getpid(), flattened_index))

    mask_trick = np.ones((winSize, winSize, winSize), dtype=np.int)
    maskITK = sitk.GetImageFromArray(mask_trick)

    extractor = featureextractor.RadiomicsFeaturesExtractor(paramPath)

    imageITK = sitk.GetImageFromArray(volume)
    imageITK.origin = origin
    imageITK.spacing = spacing
    imageITK.direction = direction

    new_row = {}

    featureVector = extractor.execute(imageITK, maskITK)  # allways is used the same mask
    # print("Result type: {} and length: {}".format(type(featureVector), len(featureVector)))  # result is returned in a Python ordered dictionary)
    # print('')
    # print('Calculated features')
    for featureName in featureVector.keys():  # Note that featureVectors is a 'disordered dictionary'
        # print('Computed %s: %s' % (featureName, featureVector[featureName]))
        # print(featureVector[featureName])
        if ('firstorder' in featureName) or ('glszm' in featureName) or \
                ('glcm' in featureName) or ('glrlm' in featureName) or \
                ('gldm' in featureName):
            new_row.update({featureName: featureVector[featureName]})

    lst = sorted(new_row.items())  # Ordering the new_row dictionary

    # Adding some columns and values at the front of the list
    # label_value = mask[z, x, y]
    lst.insert(0, ('label', label_value))
    lst.insert(0, ('axisZ', z))
    lst.insert(0, ('axisY', y))
    lst.insert(0, ('axisX', x))
    # flattened_index = np.ravel_multi_index([[z], [y], [x]], (3, 3, 3), order='F')
    #                 np.ravel_multi_index([[2],[1],[0]],rw.shape[:3])
    # [flattened_index] = np.ravel_multi_index([[x], [y], [z]], (max_x, max_y, max_z))  # order='C'
    lst.insert(0, ('flattened_index', int(flattened_index)))
    lst.insert(0, ('lessionID', lessionID))
    lst.insert(0, ('caseID', caseID))
    lst.insert(0, ('mask_filename', mask_filename))
    lst.insert(0, ('image_filename', image_filename))

    od = OrderedDict(lst)
    # for name in od.keys():
    #     print('Computed %s: %s' % (name, od[name]))

    #print("Process {} done processing index: {}".format(os.getpid(), flattened_index))

    return (i, od)


class RadiomicParallelClass(FeatureExtractionStrategy):
    def __init__(self, name, ncores):
        self.radiomicNCores = ncores
        super().__init__(name)

    def build_mask_trick(self, window_size):
        print("Empty dummy function.")

    def build_extractor(self, paramPath):
        print("Empty dummy function.")


    def featureExtraction(self, array, mask, image_filename, mask_filename, caseID, lessionID, origin, spacing, direction):
        print("      Using Parallel Radiomic to extract features...")

        assert type(array).__module__ == np.__name__, "Error, expected a numpy object."
        assert array.ndim == 6, "Error, the array's dimension must be equal to 6."

        max_z, max_x, max_y = array.shape[:3]

        print("         max_z: {}, max_x: {}, max_y: {}".format(max_z, max_x, max_y))
        print("         Extracting new {} rows of features.".format(max_z * max_x * max_y))

        start_time = time.process_time()

        global results
        results = []

        # TODO: add parameter
        pool = mp.Pool(self.radiomicNCores)    # pool = mp.Pool(mp.cpu_count()-1)

        for x in range(max_x):  # x: row
            for y in range(max_y):  # y: column
                for z in range(max_z):  # z: deep

                    volume = array[z, x, y]     # get a cube from the array.
                    label_value = mask[z, x, y]
                    [flattened_index] = np.ravel_multi_index([[x], [y], [z]], (max_x, max_y, max_z))  # order='C'

                    winSize=3
                    paramPath = "/home/willytell/Documentos/PhD/lc3d/config/Params.yaml"
                    i = flattened_index # used to get back an ordered list.

                    pool.apply_async(do_it, args=(i, x, y, z, flattened_index, winSize, paramPath, volume, label_value,
                                    image_filename, mask_filename, caseID, lessionID, origin, spacing, direction), callback=collect_result)

        pool.close()
        pool.join()

        results.sort(key=lambda x: x[0])
        results_final = [r for i, r in results]

        df = pd.DataFrame.from_dict(results_final)

        elapsed_time = time.process_time() - start_time  # it measures in seconds
        print("      Elapsed time for Radiomic to extract features: {:.2f} seconds.".format(elapsed_time))

        return df

############################ PARALLEL COMPUTING ######################################################



def debug_test():
    vol = np.arange(216).reshape(6, 6, 6)
    # rw = rolling_window(a, (3,3,3), asteps=(1,1,2))
    rw = rolling_window(vol, (3, 3, 3), asteps=(1, 1, 1))
    #print(rw)
    print(rw.shape)

    mr = RadiomicClass('myRadiomic')
    mr.build_mask_trick(window_size=3)
    mr.build_extractor(paramPath='/home/willytell/Documentos/PhD/pyradiomics/examples/exampleSettings/Params.yaml')
    mr.featureExtraction(rw)


if __name__ == '__main__':
    debug_test()
    #test()