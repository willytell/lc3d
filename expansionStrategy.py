import numpy as np

from abc import ABC, abstractmethod

class ExpansionStrategy(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

    # count = np.zeros(ncomponents + 1)
    def count_all_labels(self, volume, ncomponents, count):
        for l in range(0, ncomponents + 1):  # include the label '0' that corresponds to background.
            count[l] = len(np.where(volume == l)[0])

    def one_label_present(self, count, label_number):
        assert label_number != 0, "UniformExpansion, one_label_present does not verify the background label."
        if count[label_number] == count[1:].sum():  # background is discarded
            # print("The label {} is the only one present in the volume.".format(label_number))
            return True
        else:
            # print("The label {} is not the only one present in the volume.".format(label_number))
            return False

    # increse in x negative direction
    def zero(self, labeled, vbbox, label_number, ncomponents, nvoxel, growth_xyz):

        lowest_idx_x = 0

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
    def one(self, labeled, vbbox, label_number, ncomponents, nvoxel, growth_xyz):

        higest_idx_x = labeled.shape[0]

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
    def two(self, labeled, vbbox, label_number, ncomponents, nvoxel, growth_xyz):

        lowest_idx_y = 0

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
    def three(self, labeled, vbbox, label_number, ncomponents, nvoxel, growth_xyz):

        higest_idx_y = labeled.shape[1]

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
    def four(self, labeled, vbbox, label_number, ncomponents, nvoxel, growth_xyz):

        lowest_idx_z = 0

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
    def five(self, labeled, vbbox, label_number, ncomponents, nvoxel, growth_xyz):

        higest_idx_z = labeled.shape[2]

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

    @abstractmethod
    def expand(self):
        pass


# Background Percentage Expansion
class UniformExpansion(ExpansionStrategy):
    def __init__(self, name, nvoxel):
        self.nvoxel = nvoxel
        super().__init__(name)

    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):
        tmp_vbbox = minimal_vbbox

        # growth_xyz represents the directions to growth: [x-, x+, y-, y+, z-, z+]
        growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)

        # Defining a dictionary with function to expand the vbbox.
        fc_dict = {0: super().zero, 1: super().one, 2: super().two, 3: super().three, 4: super().four, 5: super().five}

        print("    tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

        idx = 0
        while idx <= (len(growth_xyz) - 1):
            myfunc = fc_dict[idx]
            myfunc(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)

            idx += 1
        # end while

        print("NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
        del growth_xyz


        print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox




# Background Percentage Expansion
class Bg_pExpansion(ExpansionStrategy):
    def __init__(self, name, background_percentage, groundtruth_percentage, nvoxel, check_bg_percentage):
        self.background_percentage = background_percentage
        self.groundtruth_percentage = groundtruth_percentage
        self.nvoxel = nvoxel
        self.check_bg_percentage = check_bg_percentage
        super().__init__(name)

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
        super().count_all_labels(volume, ncomponents, count)
        print("label_number : {}".format(label_number))
        print("count = {}".format(count))
        bg_p, gt_p = self.percentage_calculation(count, label_number)
        print("Percentage of vbbox: bg_p = {:.2f}, gt_p = {:.2f}".format(round(bg_p, 2), round(gt_p, 2)))
        del count

        return bg_p, gt_p

    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):

        bg_p, _ = self.get_percentage(labeled, minimal_vbbox, ncomponents, label_number)
        tmp_vbbox = minimal_vbbox

        if bg_p < self.background_percentage:  # if it's necessary to expand the vbbox.
            stop = False
            idx = 0
            # growth_xyz represents the directions to growth: [x-, x+, y-, y+, z-, z+]
            growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)

            # Defining a dictionary with function to expand the vbbox.
            fc_dict = {0: super().zero, 1: super().one, 2: super().two, 3: super().three, 4: super().four, 5: super().five}

            print("    tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
            while idx <= (len(growth_xyz) - 1) and (not stop):
                myfunc = fc_dict[idx]
                myfunc(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)

                bg_p, _ = self.get_percentage(labeled, tmp_vbbox, ncomponents, label_number)
                if self.background_percentage <= bg_p or not np.any(growth_xyz):
                    growth_xyz[0:] = False
                    stop = True

                idx += 1
            # end while

            print("NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
            del growth_xyz
        else:
            print("Already enough background!")

        print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox

