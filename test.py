#!/usr/bin/python

import SimpleITK as sitk
import numpy as np
from scipy.ndimage.measurements import label

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Reading the mask
fname = '/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CTmask_nii/LIDC-IDRI-0001_GT1_Mask.nii.gz'
img = sitk.ReadImage(fname)

# Printing information about the mask.
print("IMAGE INFORMATION\n")
print("Origin: {}".format(img.GetOrigin))
print("Size: {}".format(img.GetSize()))
print("Spacing: {}".format(img.GetSpacing()))
print("Direction: {}".format(img.GetDirection()))

print("Dimension: {}".format(img.GetDimension()))
print("Width: {}".format(img.GetWidth()))
print("Height: {}".format(img.GetHeight()))
print("Depth: {}".format(img.GetDepth()))

print("Pixel ID Value: {}".format(img.GetPixelIDValue()))
print("Pixel ID Type As String: {}".format(img.GetPixelIDTypeAsString()))
print("Number Of Components Per Pixel: {}".format(img.GetNumberOfComponentsPerPixel()))


# CONVERTING from SimpleITK image to Numpy array
cube = sitk.GetArrayFromImage(img)

# Printing information about the numpy
print("\nImage Size: {}".format(img.GetSize()))
print("Array Shape: {}".format(cube.shape))



# LABELING
#se = generate_binary_structure(3,3,3).astype(np.int)
se = np.ones((3,3,3), dtype=np.int)
labeled, ncomponents = label(cube, se)

print("\nncomponents: {}".format(ncomponents))

# Plotting
# set the colors of each object
#colors = np.empty(labeled.shape, dtype=object)

# and plot everything
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#ax.voxels(labeled, facecolors=colors, edgecolor='k')
#plt.show()


# Volume Bounding Box for the labeled mask
def bbox2_3D(img):

    r = np.any(img, axis=(1, 2))
    c = np.any(img, axis=(0, 2))
    z = np.any(img, axis=(0, 1))

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return rmin, rmax, cmin, cmax, zmin, zmax


bbox = bbox2_3D(labeled)
print("(xmin, xmax, ymin, ymax, zmin, zmax): {}".format(bbox))

#print( labeled[bbox[0]:(bbox[1]+1), bbox[2]:(bbox[3]+1), bbox[4]:(bbox[5]+1)] )

# EXACT ROI
#volume_bbox = labeled[bbox[0]:(bbox[1]+1), bbox[2]:(bbox[3]+1), bbox[4]:(bbox[5]+1)]

# ROI with 1 extra voxel
volume_bbox = labeled[bbox[0]-1:(bbox[1]+2), bbox[2]-1:(bbox[3]+2), bbox[4]-1:(bbox[5]+2)]

# CONVERTING from Numpy to SimpleITK image
img_back = sitk.GetImageFromArray(volume_bbox)


# SAVING bbox image
# Remember to to set the image's origin, spacing, and possibly direction cosine matrix. The default values may not match the physical dimensions of your image.
img_back.SetOrigin(img.GetOrigin())
img_back.SetSpacing(img.GetSpacing())
img_back.SetDirection(img.GetDirection())
sitk.WriteImage(img_back, '/home/willytell/Escritorio/back.nii.gz')


hist, bin_edges = np.histogram(volume_bbox.flatten(), bins=np.arange(ncomponents+2), density=False)

print("hist: {}".format(hist))
print("bin_edges: {}".format(bin_edges))









