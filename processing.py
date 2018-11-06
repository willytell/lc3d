import sys
import time
from abc import ABC, abstractmethod
from input import NiftyManagement
from utils import get_components
from plugin import Labeling, VolumeBBox, ExpandVBBox, SaveVBBoxNifty
from expansionStrategy import UniformExpansion


class Processing(ABC):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.show_plugin_time = True
        self.show_total_time = True
        self.plugin_stack = []
        self.data = {}
        super().__init__()

    @abstractmethod
    def run (self):
        pass

    def execute_stack(self):
        total_time = 0

        idx = 0
        continueProcessing = True

        while idx < len(self.plugin_stack) and continueProcessing:
            plugin = self.plugin_stack[idx]
            start_time = time.process_time()  # process_time does not include time elapsed during sleep.
            continueProcessing = plugin.process(self.config, self.data)
            elapsed_time = time.process_time() - start_time  # measure in seconds
            #elapsed_time *= 1000  # to milliseconds
            if self.show_plugin_time:
                print("Elapsed time for the plugin '{}': {:.2f} seconds.".format(plugin.name, elapsed_time))
            total_time += elapsed_time
            idx += 1

        if self.show_total_time:
            print("Elapsed time for the plugins stack: {:.2f} seconds.".format(total_time))

        return continueProcessing


class VBBoxPerNoduleProcessing(Processing):
    def __init__(self, name, config):
        super().__init__(name, config)

    def build_stack(self):
        # Plugin NiftyManagement
        myNiftyManagement = NiftyManagement('myNiftyHandler', self.config.src_image_path, self.config.src_mask_path,
                        self.config.mask_pattern, self.config.dst_image_path, self.config.dst_mask_path)
        myNiftyManagement.masks2read()
        self.plugin_stack.append(myNiftyManagement)

        # Plugin Labeling
        myLabeling = Labeling('myLabeling')
        dim_x, dim_y, dim_z = get_components(self.config.labeling_se_dim)
        myLabeling.set_structure_element(dim_x, dim_y, dim_z)
        self.plugin_stack.append(myLabeling)

        # Plugin VolumeBBox
        myVolumeBBox = VolumeBBox('myVolumeBBox')
        self.plugin_stack.append(myVolumeBBox)

        # Plugin UniformExpandVBBox
        if self.config.expanionStrategy == 'uniform':
            expanionStrategy = UniformExpansion('uniform', self.config.background_p, self.config.groundtruth_p, self.config.nvoxels,
                                                   self.config.check_bg_percentage)
        # elif self.config.expanionStrategy == 'other_option':
        #     expanionStrategy = other_option()
        else:
            print("Error, config.expanionStrategy does not match any option")
            sys.exit()

        myExpandVBBox = ExpandVBBox('myExpandVBBox', expanionStrategy)
        self.plugin_stack.append(myExpandVBBox)

        # Plugin SaveVBBoxNifty
        mySaveVBBoxNifty = SaveVBBoxNifty('mySaveVBBoxNifty', self.config.dst_image_path, self.config.dst_mask_path)
        self.plugin_stack.append(mySaveVBBoxNifty)

    def run(self):
        print("Running VBBoxPerNoduleProcessing...")
        continueProcessing = True

        while continueProcessing:
            continueProcessing = super().execute_stack()
            print("--------------------------------------------------------------------")



def debug_test():
    from configuration import Configuration

    config = Configuration("config/conf_extractfeatures.py", "extract features").load()

    myVBBoxPerNoduleProcessing = VBBoxPerNoduleProcessing('myVBBoxPerNoduleProcessing', config)
    myVBBoxPerNoduleProcessing.build_stack()
    myVBBoxPerNoduleProcessing.run()


if __name__ == '__main__':
    debug_test()



