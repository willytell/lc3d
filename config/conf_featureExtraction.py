# DB TYPE
#db_type                = "COMPRESSED NIFTY"   # [ "DICOM" | "NIFTY" | "COMPRESSED NIFTY"]


# DB SOURCE PATHS
src_image_path          = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/CTRoi_nii"
src_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/CTRoimask_nii"

mask_pattern            = '*.nii.gz'

# OUTPUT PATHS
dst_image_path          = None
dst_mask_path           = None


# Labeling
labeling_se_dim         = '(3, 3, 3)'   # Labeling structure_element dimension

# Strategy to expand the VolumeBBox
expanionStrategy        = 'uniform'     # ['uniform' | 'uniform checking bg']
background_p            = 55
groundtruth_p           = 45
nvoxels                 = 1             # Amount of voxels to increment in each step.
check_bg_percentage     = True          # Check the background percentage during the expansion

# Sliding Window
window_size             = 3             # [3 | 5 | 7 | 9 | 11 | so on ]. For example, 3 means a volume of 3x3x3.
deltaX                  = 1             # slide n voxel in x direction
deltaY                  = 1             # slide m voxel in y direction
deltaZ                  = 1             # slide l voxel in z direction
mode                    = 'edge'        # ['constant'|'edge'|'mean'| etc.] Look inside np.pad() for all the modes.

# Radiomic
radiomicConfigFile      = "/home/willytell/Documentos/PhD/lc3d/config/Params.yaml"
