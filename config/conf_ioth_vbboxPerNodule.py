# DB TYPE
#db_type                = "COMPRESSED NIFTI"   # [ "DICOM" | "NIFTI" | "COMPRESSED NIFTI"]


# DB SOURCE PATHS
src_image_path          = "/media/willytell/TOSHIBA EXT/LungCTDataBase/LIDC-IDRI/Nii_Vol/CT_nii"
src_mask_path           = "/media/willytell/TOSHIBA EXT/LungCTDataBase/LIDC-IDRI/Nii_Vol/CTmask_nii"

# Set internal_input = 1 if image and mask have the following string pattern:
#  Image filename: LIDC-IDRI-0001_GT1.nii.gz
#  Mask filename:  LIDC-IDRI-0001_GT1_Mask.nii.gz
# OR
# Set internal_input = 2 if image and mask have the following string pattern:
#  Image filename: LIDC-IDRI-0001_GT1_1.nii.gz
#  Mask filename:  LIDC-IDRI-0001_GT1_1_Mask.nii.gz
internal_input          = 1

mask_pattern            = '*.nii.gz'

# OUTPUT PATHS
dst_image_path          = "/home/willytell/Escritorio/LungCTDataBase/ioth/Nii_Vol/CTRoi_nii"
dst_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/ioth/Nii_Vol/CTRoimask_nii"


# Labeling
labeling_se_dim         = '(3, 3, 3)'   # Labeling structure_element dimension

# Strategy to expand the VolumeBBox
expanionStrategy        = 'Uniform'   # ['Uniform' | 'AnyGrowth' | 'Background-percentage' | 'physicianDelta']
background_p            = 55
groundtruth_p           = 45
nvoxels                 = 1 #[1, 7]     # int or sequence: int | [1, 5]
limit                   = [25, 35]      # Maximum amount of voxels to be increased to the ROI.

bg_p_nvoxels            = 1             # Bg_p Expansion: amount of voxels to increment in each step.
check_bg_percentage     = True          # Check the background percentage during the expansion

# physicianDeltaExpansion
physicianDelta_expand_x = [2, 2]      # [expandX1, expandX2]
physicianDelta_expand_y = [25, 25]
physicianDelta_expand_z = [25, 25]

physicianDelta_growth_x = 1             # int to increase in x axis
physicianDelta_growth_y = 1
physicianDelta_growth_z = 1

# random delta
physicianDelta_delta_x  = None #[1, 1]        # [None | [deltaX1, deltaX2]] => used to [(expandX1 +/- deltaX1), (expandX2 +/- deltaX2)]
physicianDelta_delta_y  = [5, 5]
physicianDelta_delta_z  = [5, 5]


# Sliding Window
window_size             = 3             # [3 | 5 | 7 | 9 | 11 | so on ]. For example, 3 means a volume of 3x3x3.
deltaX                  = 1             # slide n voxel in x direction
deltaY                  = 1             # slide m voxel in y direction
deltaZ                  = 1             # slide l voxel in z direction
mode                    = 'edge'        # ['constant'|'edge'|'mean'| etc.] Look inside np.pad() for all the modes.

# Radiomic
radiomicConfigFile      = "/home/willytell/Documentos/PhD/lc3d/config/Params.yaml"
