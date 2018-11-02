

# Input: dimension = '(3,3,3)'
# Output: 3, 3, 3
def get_components(dimension):
    dimension = dimension.replace('(','')  # remove '('
    dimension = dimension.replace(')','')  # remove ')'
    dimension = dimension.split(',')
    return int(dimension[0]), int(dimension[1]), int(dimension[2])

