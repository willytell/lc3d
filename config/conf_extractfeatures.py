# DB TYPE
#db_type                = "COMPRESSED NIFTY"   # [ "DICOM" | "NIFTY" | "COMPRESSED NIFTY"]


# DB SOURCE PATHS
src_image_path          = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CT_nii"
src_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CTmask_nii"

mask_pattern            = '*.nii.gz'

# OUTPUT PATHS
dst_image_path          = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/CT_nii"
dst_mask_path           = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/CTmask_nii"


# Labeling
labeling_se_dim         = '(3, 3, 3)' # Labeling structure_element dimension





background              = 50
groundtruth             = 50

# fix de amount of voxels in x, y, and z direction
plus_x = None
plus_y = None
plus_z = None