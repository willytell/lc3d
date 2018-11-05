# DB TYPE
#db_type                = "COMPRESSED NIFTY"   # [ "DICOM" | "NIFTY" | "COMPRESSED NIFTY"]


# DB SOURCE PATHS
src_image_path          = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CT_nii"
src_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CTmask_nii"

mask_pattern            = '*.nii.gz'

# OUTPUT PATHS
dst_image_path          = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/CTRoi_nii"
dst_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/CTRoimask_nii"


# Labeling
labeling_se_dim         = '(3, 3, 3)'   # Labeling structure_element dimension

# Strategy to expand the VolumeBBox
expanionStrategy        = 'uniform'     # ['uniform' | 'uniform checking bg']
background_p            = 55
groundtruth_p           = 45
nvoxels                 = 1             # Amount of voxels to increment in each step.
check_bg_percentage     = True          # Check the background percentage during the expansion

# fix de amount of voxels in x, y, and z direction
plus_x = None
plus_y = None
plus_z = None