import numpy as np

class SlidingWindow():

    def __init__(self, window_size, mode='edge', window=(0,), asteps=None, wsteps=None, axes=None, toend=True):
        self.window_size = window_size   # with a window_size of 3, it indicates a 3x3x3 window.
        self.mode = mode  # determine the mode to pad

        #parameters used in rolling_window()
        self.window = window
        self.asteps = asteps
        self.wsteps = wsteps
        self.axes = axes
        self.toend = toend


    def get_slices_to_add(self, window_size):
        """
        This function has been coded to be used with a 3D window, like 3x3x3, 5x5x5, 7x7x7, 9x9x9, and so on.
        In the case of 3x3x3, window_dimension should be equal to 3,
                   for 5x5x5, window_dimension should be equal to 5,
                   for 7x7x7, window_dimension should be equal to 7, and so on.

        """
        assert window_size >= 3, "Error, the minimum window dimension allowed is 3."
        assert divmod(window_size, 2)[1] == 1, "Error, window dimension must be odd."

        slice = 1  # amount of slice(s) to add to the volume
        wsize = 3    # minimum size of the window is 3x3x3.

        while wsize != window_size:
            wsize += 2
            slice += 1

        return slice


    def padding(self, volume):
        slices = self.get_slices_to_add(self.window_size)

        if volume.ndim == 3:
            to_add = np.array([[1,1], [1,1], [1,1]])
            #volume = np.pad(volume, slices * to_add, self.mode)
            #print("The Volume has been padded using the method: '{}'.".format(self.mode))
        else:
            print("Error in dimension of the volume.")
            raise 1 == 0

        return np.pad(volume, slices * to_add, self.mode)


    def rolling_window(self, array):
        # check if window * wsteps is smaller than 'array'.
        result = self.real_rolling_window(array, self.window, self.asteps, self.wsteps, self.axes, self.toend)
        return result


    def real_rolling_window(self, array, window = (0,), asteps = None, wsteps = None, axes = None, toend = True):
        """
        Credits of this function to Sebastian Berg, https://gist.github.com/seberg/3430219

        Create a view of `array` which for every point gives the n-dimensional
        neighbourhood of size window. New dimensions are added at the end of
        `array` or after the corresponding original dimension.

        Parameters
        ----------
        array : array_like
            Array to which the rolling window is applied.
        self.window : int or tuple
            Either a single integer to create a window of only the last axis or a
            tuple to create it for the last len(window) axes. 0 can be used as a
            to ignore a dimension in the window.
        self.asteps : tuple
            Aligned at the last axis, new steps for the original array, ie. for
            creation of non-overlapping windows. (Equivalent to slicing result)
        self.wsteps : int or tuple (same size as window)
            steps for the added window dimensions. These can be 0 to repeat values
            along the axis.
        self.axes: int or tuple
            If given, must have the same size as window. In this case window is
            interpreted as the size in the dimension given by axes. IE. a window
            of (2, 1) is equivalent to window=2 and axis=-2.
        self.toend : bool
            If False, the new dimensions are right after the corresponding original
            dimension, instead of at the end of the array. Adding the new axes at the
            end makes it easier to get the neighborhood, however toend=False will give
            a more intuitive result if you view the whole array.

        Returns
        -------
        A view on `array` which is smaller to fit the windows and has windows added
        dimensions (0s not counting), ie. every point of `array` is an array of size
        window.

        Examples
        --------
        # >>> a = np.arange(9).reshape(3,3)
        # >>> rolling_window(a, (2,2))
        array([[[[0, 1],
                 [3, 4]],
                [[1, 2],
                 [4, 5]]],
               [[[3, 4],
                 [6, 7]],
                [[4, 5],
                 [7, 8]]]])

        Or to create non-overlapping windows, but only along the first dimension:
        # >>> rolling_window(a, (2,0), asteps=(2,1))
        array([[[0, 3],
                [1, 4],
                [2, 5]]])

        Note that the 0 is discared, so that the output dimension is 3:
        # >>> rolling_window(a, (2,0), asteps=(2,1)).shape
        (1, 3, 2)

        This is useful for example to calculate the maximum in all (overlapping)
        2x2 submatrixes:
        # >>> rolling_window(a, (2,2)).max((2,3))
        array([[4, 5],
               [7, 8]])

        Or delay embedding (3D embedding with delay 2):
        # >>> x = np.arange(10)
        # >>> rolling_window(x, 3, wsteps=2)
        array([[0, 2, 4],
               [1, 3, 5],
               [2, 4, 6],
               [3, 5, 7],
               [4, 6, 8],
               [5, 7, 9]])
        """

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
            #print("ValueError: `window` must be one-dimensional.")
            #return None
        if np.any(window < 0):
            raise ValueError("All elements of `window` must be larger then 1.")
            #print("ValueError: All elements of `window` must be larger then 1.")
            #return None
        if len(array.shape) < len(window):
            raise ValueError("`window` length must be less or equal `array` dimension.")
            #print("ValueError: `window` length must be less or equal `array` dimension.")
            #return None

        _asteps = np.ones_like(orig_shape)
        if asteps is not None:
            asteps = np.atleast_1d(asteps)
            if asteps.ndim != 1:
                raise ValueError("`asteps` must be either a scalar or one dimensional.")
                #print("ValueError: `asteps` must be either a scalar or one dimensional.")
                #return None
            if len(asteps) > array.ndim:
                raise ValueError("`asteps` cannot be longer then the `array` dimension.")
                #print("ValueError: `asteps` cannot be longer then the `array` dimension.")
                #return None
            # does not enforce alignment, so that steps can be same as window too.
            _asteps[-len(asteps):] = asteps

            if np.any(asteps < 1):
                raise ValueError("All elements of `asteps` must be larger then 1.")
                #print("ValueError: All elements of `asteps` must be larger then 1.")
                #return None
        asteps = _asteps

        _wsteps = np.ones_like(window)
        if wsteps is not None:
            wsteps = np.atleast_1d(wsteps)
            if wsteps.shape != window.shape:
                raise ValueError("`wsteps` must have the same shape as `window`.")
                #print("ValueError: `wsteps` must have the same shape as `window`.")
                #return None
            if np.any(wsteps < 0):
                raise ValueError("All elements of `wsteps` must be larger then 0.")
                #print("ValueError: All elements of `wsteps` must be larger then 0.")
                #return None

            _wsteps[:] = wsteps
            _wsteps[window == 0] = 1  # make sure that steps are 1 for non-existing dims.
        wsteps = _wsteps

        # Check that the window would not be larger then the original:
        if np.any(orig_shape[-len(window):] < window * wsteps):
            #raise ValueError("`window` * `wsteps` larger then `array` in at least one dimension.")
            print("ValueError: `window` * `wsteps` larger then `array` in at least one dimension.")
            return None

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