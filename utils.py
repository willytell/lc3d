
# Input: dimension = '(3,3,3)'
# Output: 3, 3, 3
def get_components(dimension):
    dimension = dimension.replace('(','')  # remove '('
    dimension = dimension.replace(')','')  # remove ')'
    dimension = dimension.split(',')
    return int(dimension[0]), int(dimension[1]), int(dimension[2])

# Input: filename = LIDC-IDRI-0005_GT1_Mask.nii.gz , label = 1
# Output: for image_filename = LIDC-IDRI-0005_GT1_<label>.nii.gz      => LIDC-IDRI-0005_GT1_1.nii.gz
#         for mask_filename = LIDC-IDRI-0005_GT1_<label>_Mask.nii.gz  => LIDC-IDRI-0005_GT1_1_Mask.nii.gz
def get_dst_filename_nifti(filename, label):
    name_splitted = filename.split('.')[0].split('_')
    mask_filename = name_splitted[0] + '_' + name_splitted[1] + '_' + str(label) + '_' + name_splitted[2] + '.nii.gz'
    image_filename = name_splitted[0] + '_' + name_splitted[1] + '_' + str(label) + '.nii.gz'
    return image_filename, mask_filename
