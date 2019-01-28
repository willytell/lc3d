import numpy as np
from random import randint, random

from abc import ABC, abstractmethod

class ExpansionStrategy(ABC):
    def __init__(self, name):
        self.name = name
        super().__init__()

    # count = np.zeros(ncomponents + 1)
    def count_all_labels(self, volume, ncomponents, count):
        # print("volume.max: {}".format(volume.max()))
        # print("volume.min: {}".format(volume.min()))
        #
        # unique, counts = np.unique(volume, return_counts=True)
        # print("unique : {}".format(unique))
        # print("counts : {}".format(counts))

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


                print(volume[50:60, 50:60, :])

                unique, counts = np.unique(volume, return_counts=True)
                print("unique : {}".format(unique))
                print("counts : {}".format(counts))


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

class UniformExpansion(ExpansionStrategy):
    def __init__(self, name, nvoxel, limit):

        if type(nvoxel) is list:
            # nvoxel is a range
            assert len(nvoxel) == 2, "The range must be determined by to integers."
            assert nvoxel[0] < nvoxel[1], "To specify a range: the first number must be less than the second one."
            assert nvoxel[0] > 0, "Must increase at least one voxel."
            self.nvoxel_range = nvoxel
        else:
            # nvoxel is an int
            self.nvoxel_range = None

        if type(limit) is list:
            # limit is a range
            assert len(limit) == 2, "Limit: the range must be determined by to integers."
            assert limit[0] < limit[1], "Limit: to specify a range: the first number must be less than the second one."
            assert limit[0] > 0, "Limit: must increase at least one voxel."
            self.nvoxel_limit = limit
        else:
            # limit is an int
            self.nvoxel_limit = None

        self.nvoxel = nvoxel
        self.limit = limit
        super().__init__(name)

    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):
        tmp_vbbox = minimal_vbbox

        # if nvoxel is a sequence, this is a range from where a number must be selected randomly. Then this number
        # will be used to increase the ROI.
        if self.nvoxel_range is not None:
            self.nvoxel = randint(self.nvoxel_range[0], self.nvoxel_range[1])
            print("      Number of Voxels to increase the vbbox: {}".format(self.nvoxel))

        if self.nvoxel_limit is not None:
            self.limit = randint(self.nvoxel_limit[0], self.nvoxel_limit[1])
            print("      Maximum number of voxels to increase the vbbox: {}".format(self.limit))

        # growth_xyz represents the directions to make the growth: [x-, x+, y-, y+, z-, z+]
        growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)

        # Defining a dictionary with function to expand the vbbox.
        fc_dict = {0: super().zero, 1: super().one, 2: super().two, 3: super().three, 4: super().four, 5: super().five}

        print("          tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

        stop = False
        total_sum = 0

        while not stop:
            idx = 0
            backup_lst = tmp_vbbox
            while idx <= (len(growth_xyz) - 1):
                myfunc = fc_dict[idx]
                myfunc(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)

                idx += 1
            # end while

            if np.all(growth_xyz):
                total_sum += self.nvoxel
                backup_lst = tmp_vbbox
                print("      NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

            if not np.all(growth_xyz) or self.limit <= total_sum:
                stop = True

        del growth_xyz
        tmp_vbbox = backup_lst

        #print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox



class AnyExpansion(ExpansionStrategy):
    """Increase the size of the ROI in any direction x, y, and z."""

    def __init__(self, name, nvoxel, limit):
        """
        Params
        ------
        name : str
            Name of the object
        nvoxel : int or sequence of two int that indicates a range
            With a number it is the amount to increase in each iteration the ROI. If this is a sequence of two numbers,
            it represents a range from where a number will be selected randomly to increase in each iteration the ROI.
        limit : int or sequence of two int that indicates a range
            Indicates how many voxels should be increased to the ROI. If this is a sequence (range), a random number
            will be selected between the range to be used as limit.
        """

        if type(nvoxel) is list:
            # nvoxel is a range
            assert len(nvoxel) == 2, "nvoxel: the range must be determined by to integers."
            assert nvoxel[0] < nvoxel[1], "To specify a range: the first number must be less than the second one."
            assert nvoxel[0] > 0, "Must increase at least one voxel."
            self.nvoxel_range = nvoxel
        else:
            # nvoxel is an int
            self.nvoxel_range = None

        if type(limit) is list:
            # limit is a range
            assert len(limit) == 2, "Limit: the range must be determined by to integers."
            assert limit[0] < limit[1], "Limit: to specify a range: the first number must be less than the second one."
            assert limit[0] > 0, "Limit: must increase at least one voxel."
            self.nvoxel_limit = limit
        else:
            # limit is an int
            self.nvoxel_limit = None

        self.nvoxel = nvoxel
        self.limit = limit
        super().__init__(name)

    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):
        tmp_vbbox = minimal_vbbox

        # if nvoxel is a sequence, this is a range from whrere a number must be selected randomly. Then this number
        # will be used to increase the ROI.
        if self.nvoxel_range is not None:
            self.nvoxel = randint(self.nvoxel_range[0], self.nvoxel_range[1])
            print("      Number of Voxels to increase the vbbox: {}".format(self.nvoxel))

        if self.nvoxel_limit is not None:
            self.limit = randint(self.nvoxel_limit[0], self.nvoxel_limit[1])
            print("      Maximum number of voxels to increase the vbbox: {}".format(self.limit))

        # growth_xyz represents the directions to make the growth: [x-, x+, y-, y+, z-, z+]
        growth_xyz = np.array([True, True, True, True, True, True], dtype=np.bool)

        # Defining a dictionary with function to expand the vbbox.
        fc_dict = {0: super().zero, 1: super().one, 2: super().two, 3: super().three, 4: super().four, 5: super().five}

        print("          tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

        stop = False
        total_sum = 0

        while not stop:
            idx = 0
            while idx <= (len(growth_xyz) - 1):
                myfunc = fc_dict[idx]
                myfunc(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)

                idx += 1
            # end while

            print("      NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

            if np.any(growth_xyz):
                total_sum += self.nvoxel

            if not np.any(growth_xyz) or self.limit <= total_sum:
                stop = True

        del growth_xyz

        #print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox




# Background Percentage Expansion
class Bg_pExpansion(ExpansionStrategy):
    def __init__(self, name, background_percentage, groundtruth_percentage, nvoxel, check_bg_percentage):
        self.background_percentage = background_percentage
        self.groundtruth_percentage = groundtruth_percentage
        self.nvoxel = nvoxel
        assert type(nvoxel) is int, "With Backgroun-percentage, nvoxel must be an integer."
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
        #print("    Label : {}".format(label_number))
        print("      count = {}".format(count))
        bg_p, gt_p = self.percentage_calculation(count, label_number)
        print("      Percentage of vbbox: bg_p = {:.2f}, gt_p = {:.2f}".format(round(bg_p, 2), round(gt_p, 2)))
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

            print("          tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
            while idx <= (len(growth_xyz) - 1) and (not stop):
                myfunc = fc_dict[idx]
                myfunc(labeled, tmp_vbbox, label_number, ncomponents, self.nvoxel, growth_xyz)

                bg_p, _ = self.get_percentage(labeled, tmp_vbbox, ncomponents, label_number)
                if self.background_percentage <= bg_p or not np.any(growth_xyz):
                    growth_xyz[0:] = False
                    stop = True

                idx += 1
            # end while

            print("      NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))
            del growth_xyz
        else:
            print("      Already enough background!")

        print("    Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox


class PhysicianDeltaExpansion(ExpansionStrategy):
    def __init__(self, name, expand_x, expand_y, expand_z, growth_x, growth_y, growth_z, delta_x, delta_y, delta_z):
        self.expand_x = expand_x
        self.expand_y = expand_y
        self.expand_z = expand_z
        self.growth_x = growth_x
        self.growth_y = growth_y
        self.growth_z = growth_z
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.delta_z = delta_z
        super().__init__(name)


    def findExpansionLimits(self):

        #### calculate the limits for X ###
        Xn1 = self.expand_x[0]
        Xn2 = self.expand_x[1]

        if self.delta_x is not None:
            delta_Xn1 = self.delta_x[0]
            sign = 1 if random() < 0.5 else -1
            tmp = Xn1 + sign * randint(0, delta_Xn1)
            Xn1 = tmp if 0 < tmp else 0

            delta_Xn2 = self.delta_x[1]
            sign = 1 if random() < 0.5 else -1
            tmp = Xn2 + sign * randint(0, delta_Xn2)
            Xn2 = tmp if 0 < tmp else 0

        #### calculate the limits for Y ###
        Ym1 = self.expand_y[0]
        Ym2 = self.expand_y[1]

        if self.delta_y is not None:
            delta_Ym1 = self.delta_y[0]
            sign = 1 if random() < 0.5 else -1
            tmp = Ym1 + sign * randint(0, delta_Ym1)
            Ym1 = tmp if 0 < tmp else 0

            delta_Ym2 = self.delta_y[1]
            sign = 1 if random() < 0.5 else -1
            tmp = Ym2 + sign * randint(0, delta_Ym2)
            Ym2 = tmp if 0 < tmp else 0

        #### calculate the limits for Z ###
        Zq1 = self.expand_z[0]
        Zq2 = self.expand_z[1]

        if self.delta_z is not None:
            delta_Zq1 = self.delta_z[0]
            sign = 1 if random() < 0.5 else -1
            tmp = Zq1 + sign * randint(0, delta_Zq1)
            Zq1 = tmp if 0 < tmp else 0

            delta_Zq2 = self.delta_z[1]
            sign = 1 if random() < 0.5 else -1
            tmp = Zq2 + sign * randint(0, delta_Zq2)
            Zq2 = tmp if 0 < tmp else 0


        return Xn1, Xn2, Ym1, Ym2, Zq1, Zq2



    def expand(self, labeled, minimal_vbbox, ncomponents, label_number):
        tmp_vbbox = minimal_vbbox

        Xn1, Xn2, Ym1, Ym2, Zq1, Zq2 = self.findExpansionLimits()

        # if it is bigger than zero, then we should try to expand the vbbox in that direction.
        a = True if Xn1 != 0 else False
        b = True if Xn2 != 0 else False
        c = True if Ym1 != 0 else False
        d = True if Ym2 != 0 else False
        e = True if Zq1 != 0 else False
        f = True if Zq2 != 0 else False

        # growth_xyz represents the directions to make the growth: [x-, x+, y-, y+, z-, z+]
        growth_xyz = np.array([a, b, c, d, e, f], dtype=np.bool)

        # Defining a dictionary with function to expand the vbbox.
        fc_dict = {0: super().zero, 1: super().one, 2: super().two, 3: super().three, 4: super().four, 5: super().five}

        print("      expand in x-, x+, y-, y+, z-, z+: {}, {}, {}, {}, {}, {}".format(Xn1, Xn2, Ym1, Ym2, Zq1, Zq2))
        print("      growth in x, y, z: {}, {}, {}".format(self.growth_x, self.growth_y, self.growth_z))
        print("      tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))

        stop = False
        total_Xn1 = 0   # x-
        total_Xn2 = 0   # x+
        total_Ym1 = 0   # y-
        total_Ym2 = 0   # y+
        total_Zq1 = 0   # z-
        total_Zq2 = 0   # z+

        while not stop:

            super().zero(labeled, tmp_vbbox, label_number, ncomponents, self.growth_x, growth_xyz)    # x-
            super().one(labeled, tmp_vbbox, label_number, ncomponents, self.growth_x, growth_xyz)     # x+

            super().two(labeled, tmp_vbbox, label_number, ncomponents, self.growth_y, growth_xyz)     # y-
            super().three(labeled, tmp_vbbox, label_number, ncomponents, self.growth_y, growth_xyz)   # y+

            super().four(labeled, tmp_vbbox, label_number, ncomponents, self.growth_z, growth_xyz)    # z-
            super().five(labeled, tmp_vbbox, label_number, ncomponents, self.growth_z, growth_xyz)    # z+


            ### x- ###
            if growth_xyz[0]:
                total_Xn1 += self.growth_x

            if (Xn1 == total_Xn1) or (Xn1 < (total_Xn1 + self.growth_x)):
                growth_xyz[0] = False

            ### x+ ###
            if growth_xyz[1]:
                total_Xn2 += self.growth_x

            if (Xn2 == total_Xn2) or (Xn2 < (total_Xn2 + self.growth_x)):
                growth_xyz[1] = False

            ### y- ###
            if growth_xyz[2]:
                total_Ym1 += self.growth_y

            if (Ym1 == total_Ym1) or (Ym1 < (total_Ym1 + self.growth_y)):
                growth_xyz[2] = False

            ### y+ ###
            if growth_xyz[3]:
                total_Ym2 += self.growth_y

            if (Ym2 == total_Ym2) or (Ym2 < (total_Ym2 + self.growth_y)):
                growth_xyz[3] = False

            ### z- ###
            if growth_xyz[4]:
                total_Zq1 += self.growth_z

            if (Zq1 == total_Zq1) or (Zq1 < (total_Zq1 + self.growth_z)):
                growth_xyz[4] = False

            ### z+ ###
            if growth_xyz[5]:
                total_Zq2 += self.growth_z

            if (Zq2 == total_Zq2) or (Zq2 < (total_Zq2 + self.growth_z)):
                growth_xyz[5] = False


            print("      NEW tmp_vbbox (xmin, xmax, ymin, ymax, zmin, zmax) = ({})".format(tmp_vbbox))


            if not np.any(growth_xyz):
                stop = True

        del growth_xyz

        #print("Expanded vbbox: {}".format(tmp_vbbox))
        return tmp_vbbox


