import numpy as np

from abc import ABC, abstractmethod

class ExpansionStrategy(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

        @abstractmethod
        def expand(self):
            pass


class UniformExpansion(ExpansionStrategy):
    def __init__(self, name, background_percentage, groundtruth_percentage, nvoxel, check_bg_percentage):
        self.background_percentage = background_percentage
        self.groundtruth_percentage = groundtruth_percentage
        self.nvoxel = nvoxel
        self.check_bg_percentage = check_bg_percentage
        self.expanded_vbbox_list = []
        super().__init__(name)

    #count = np.zeros(ncomponents + 1)
    def count_all_labels(self, volume, ncomponents, count):
        for l in range(0, ncomponents + 1):   # include the label '0' that corresponds to background.
            count[l] = len(np.where(volume == l)[0])

    def one_label_present(self, count, label_number):
        assert label_number != 0, "UniformExpand, one_label does not verify one label for background."
        if count[label_number] == count[1:].sum():  # background is discarded
            #print("The label {} is the only one present in the volume.".format(label_number))
            return True
        else:
            #print("The label {} is not the only one present in the volume.".format(label_number))
            return False

    # Must be only background and one label present in the volume.
    def percentage_calculation(self, count, label_number):
        bg_p = (count[0] * 100.0) / count.sum()   # background percentage
        gt_p = (count[label_number] * 100.0) / count.sum()  # groundtruth percentage
        return bg_p, gt_p

    def get_percentage(self, labeled, vbbox, ncomponents, label_number):
        count = np.zeros((ncomponents + 1), dtype=np.int)
        volume = labeled[vbbox[0]:vbbox[1] + 1, \
                         vbbox[2]:vbbox[3] + 1, \
                         vbbox[4]:vbbox[5] + 1]
        self.count_all_labels(volume, ncomponents, count)
        print("label_number : {}".format(label_number))
        print("count = {}".format(count))
        bg_p, gt_p = self.percentage_calculation(count, label_number)
        print("Percentage of vbbox: bg_p = {:.2f}, gt_p = {:.2f}".format(round(bg_p, 2), round(gt_p, 2)))
        del count

        return bg_p, gt_p


    def uniform_expansion(self, labeled, initial_vbbox, label_number, ncomponents, nvoxel, growth_xyz):
        #def expand(self, labeled, minimal_bbox, label_number, ncomponents, nvoxel, growth_xyz):


    #####################################################################################################
    #                                                                                                   #
    #   We define five function, one for each direction in which is posible to increase the vbbox.      #
    #                                                                                                   #
    #   # increse in x negative direction                                                               #
        def zero():
            if growth_xyz[0]:
                if lowest_idx_x <= (vbbox[0] - nvoxel):
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[(vbbox[0]-nvoxel):vbbox[1]+1, vbbox[2]:vbbox[3]+1, vbbox[4]:vbbox[5]+1]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[0] -= nvoxel
                    else:
                        growth_xyz[0] = False
                    del count
                else:
                    growth_xyz[0] = False

        # increse in x positive direction
        def one ():
            if growth_xyz[1]:
                if (vbbox[1] + nvoxel) < higest_idx_x:
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + nvoxel + 1), vbbox[2]:(vbbox[3] + 1), vbbox[4]:(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[1] += nvoxel
                    else:
                        growth_xyz[1] = False
                    del count
                else:
                    growth_xyz[1] = False

        # increse in y negative direction
        def two():
            if growth_xyz[2]:
                if lowest_idx_y <= (vbbox[2] - nvoxel):
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), (vbbox[2] - nvoxel):(vbbox[3] + 1), vbbox[4]:(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[2] -= nvoxel
                    else:
                        growth_xyz[2] = False
                    del count
                else:
                    growth_xyz[2] = False

        # increse in y positive direction
        def three():
            if growth_xyz[3]:
                if (vbbox[3] + nvoxel) < higest_idx_y:
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), vbbox[2]:(vbbox[3] + nvoxel + 1), vbbox[4]:(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[3] += nvoxel
                    else:
                        growth_xyz[3] = False
                    del count
                else:
                    growth_xyz[3] = False


        # increse in z negative direction
        def four():
            if growth_xyz[4]:
                if lowest_idx_z <= (vbbox[4] - nvoxel):
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), vbbox[2]:(vbbox[3] + 1), (vbbox[4] - nvoxel):(vbbox[5] + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[4] -= nvoxel
                    else:
                        growth_xyz[4] = False
                    del count
                else:
                    growth_xyz[4] = False

        # increse in z positive direction
        def five():
            if growth_xyz[5]:
                if (vbbox[5] + nvoxel) < higest_idx_z:
                    count = np.zeros((ncomponents + 1), dtype=np.int)
                    volume = labeled[vbbox[0]:(vbbox[1] + 1), vbbox[2]:(vbbox[3] + 1), vbbox[4]:(vbbox[5] + nvoxel + 1)]
                    self.count_all_labels(volume, ncomponents, count)
                    if self.one_label_present(count, label_number):
                        vbbox[5] += nvoxel
                    else:
                        growth_xyz[5] = False
                    del count
                else:
                    growth_xyz[5] = False


    #                                                                                                   #
    #       End of the five function definition                                                         #
    #                                                                                                   #
    #####################################################################################################



        vbbox = initial_vbbox

        lowest_idx_x = 0
        higest_idx_x = labeled.shape[0]

        lowest_idx_y = 0
        higest_idx_y = labeled.shape[1]

        lowest_idx_z = 0
        higest_idx_z = labeled.shape[2]

        # Defining a dictionary with function to expand the vbbox.
        fc_dict = {0:zero, 1:one, 2:two, 3:three, 4:four, 5:five}

        stop = False
        idx = 0
        while idx < (len(growth_xyz)-1) and (not stop):
            myfunc = fc_dict[idx]
            myfunc()

            if self.check_bg_percentage:
                bg_p, _ = self.get_percentage(labeled, vbbox, ncomponents, label_number)
                if bg_p > self.background_percentage:
                    growth_xyz[0:] = False
                    stop = True

            idx += 1

        return vbbox


    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):

        bg_p, _ = self.get_percentage(labeled, minimal_vbbox, ncomponents, label_number)
        tmp_vbbox = minimal_vbbox

        if bg_p < self.background_percentage:  # if it's necessary to expand the vbbox.
            stop = False
            # growth_xyz represents the directions to growth: [x-, x+, y-, y+, z-, z+]
            growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)

            while not stop:
                print("    tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
                tmp_vbbox = self.uniform_expansion(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)
                print("NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

                bg_p, _ = self.get_percentage(labeled, tmp_vbbox, ncomponents, label_number)
                if self.background_percentage <= bg_p or not np.any(growth_xyz):
                    stop = True

            del growth_xyz
        else:
            print("Already enough background!")


        print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox
