# DB TYPE
db_type                = "COMPRESSED NIFTY"   # [ "DICOM" | "NIFTY" | "COMPRESSED NIFTY"]

# DB SOURCE PATHS
input_db_path           = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CT_nii"
input_db_mask_path      = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/CTmask_nii"

# OUTPUT PATHS
output_db_path          = "/home/willytell/Escritorio/LungCTDataBase/lc3d/Nii_Vol/Output_CT_nii"
output_db_mask_path     = "/home/willytell/Escritorio/LungCTDataBase/Nii_Vol/Output_CTmask_nii"



background              = 50
groundtruth             = 50

# fix de amount of voxels in x, y, and z direction
plus_x = None
plus_y = None
plus_z = None