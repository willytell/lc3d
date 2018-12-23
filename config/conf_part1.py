# DB TYPE
#db_type                = "COMPRESSED NIFTI"   # [ "DICOM" | "NIFTI" | "COMPRESSED NIFTI"]


# DB SOURCE PATHS
# External storage
src_image_path          = "/media/willytell/TOSHIBA EXT/LungCTDataBase/LIDC-IDRI/Nii_Vol/CT_nii"
src_mask_path           = "/media/willytell/TOSHIBA EXT/LungCTDataBase/LIDC-IDRI/Nii_Vol/CTmask_nii"

# Local storage
#src_image_path          = "/home/willytell/Escritorio/LungCTDataBase/TMP/Nii_Vol/CTRoi_nii"
#src_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/TMP/Nii_Vol/CTRoimask_nii_parte2"

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
dst_image_path          = "/home/willytell/Escritorio/LungCTDataBase/preprocessed/Nii_Vol/CTRoi_nii"
dst_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/preprocessed/Nii_Vol/CTRoimask_nii_part1"


# Labeling
labeling_se_dim         = '(3, 3, 3)'   # Labeling structure_element dimension

# TODO: set variables by plugin.
# Strategy to expand the VolumeBBox
#expanionStrategy        = 'uniform'    # ['uniform' | 'uniform checking bg']
# UniformExpansion
uniform_nvoxels         = 1             # Uniform Expansion: amount of voxels to increment in each step.
uniform_limit           = 1             # Uniform Expansion: limit in each direction.

# Bg_pExpansion
background_p            = 50
groundtruth_p           = 50
bg_p_nvoxels            = 1             # Bg_p Expansion: amount of voxels to increment in each step.
check_bg_percentage     = True          # Check the background percentage during the expansion

# physicianDeltaExpansion
physicianDelta_expand_x = [5, 5]      # [expandX1, expandX2]
physicianDelta_expand_y = [5, 5]
physicianDelta_expand_z = [5, 5]

physicianDelta_growth_x = 1             # int to increase in x axis
physicianDelta_growth_y = 1
physicianDelta_growth_z = 1

# random delta
physicianDelta_delta_x  = None #[1, 1]        # [None | [deltaX1, deltaX2]] => used to [(expandX1 +/- deltaX1), (expandX2 +/- deltaX2)]
physicianDelta_delta_y  = None #[5, 5]
physicianDelta_delta_z  = None #[5, 5]

# Sliding Window
window_size             = 3             # [3 | 5 | 7 | 9 | 11 | so on ]. For example, 3 means a volume of 3x3x3.
deltaX                  = 1             # slide n voxel in x direction
deltaY                  = 1             # slide m voxel in y direction
deltaZ                  = 1             # slide l voxel in z direction
mode                    = 'edge'        # ['constant'|'edge'|'mean'| etc.] Look inside np.pad() for all the modes.

# Radiomic
radiomicConfigFile      = "/home/willytell/Documentos/PhD/lc3d/config/Params.yaml"
