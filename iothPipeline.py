import time
from input import NiftiManagementPlugin
from utils import get_components
from plugin import LabelPlugin, VolumeBBoxPlugin, ExpandVBBoxPlugin, SaveVBBoxNiftiPlugin
from expansionStrategy import AnyExpansion, UniformExpansion, Bg_pExpansion, PhysicianDeltaExpansion
import sys


from pipeline import Pipeline


class iothVBBoxPerNodulePipeline(Pipeline):
    def __init__(self, name, config):
        super().__init__(name, config)

    def build_stack(self):
        # Plugin NiftyManagement
        myNiftiManagement = NiftiManagementPlugin('CT',
                                                  None,
                                                  self.config.src_image_path,
                                                  self.config.src_mask_path,
                                                  self.config.mask_pattern,
                                                  self.config.dst_image_path,
                                                  self.config.dst_mask_path,
                                                  internal=self.config.internal_input)
        myNiftiManagement.masks2read()
        self.plugins_stack.append(myNiftiManagement)

        # Plugin Labeling
        myLabeling = LabelPlugin('CT_mask_labeled', [myNiftiManagement.name])
        dim_x, dim_y, dim_z = get_components(self.config.labeling_se_dim)
        myLabeling.set_structure_element(dim_x, dim_y, dim_z)
        self.plugins_stack.append(myLabeling)

        # Plugin VolumeBBox
        myVolumeBBox = VolumeBBoxPlugin('CT_mask_vbbox', [myLabeling.name])
        self.plugins_stack.append(myVolumeBBox)


        # Plugin ExpandVBBox
        myExpansion = PhysicianDeltaExpansion('physicianDeltaExpansion',
                                              self.config.physicianDelta_expand_x,
                                              self.config.physicianDelta_expand_y,
                                              self.config.physicianDelta_expand_z,
                                              self.config.physicianDelta_growth_x,
                                              self.config.physicianDelta_growth_y,
                                              self.config.physicianDelta_growth_z,
                                              self.config.physicianDelta_delta_x,
                                              self.config.physicianDelta_delta_y,
                                              self.config.physicianDelta_delta_z)


        myExpandVBBoxOne = ExpandVBBoxPlugin('CT_mask_vbbox_expansion',
                                             [myLabeling.name, myVolumeBBox.name],
                                             myExpansion)

        self.plugins_stack.append(myExpandVBBoxOne)


        # Plugin SaveVBBoxNifty
        mySaveVBBoxNifty = SaveVBBoxNiftiPlugin('SaveVBBoxNifty', [myNiftiManagement.name, myExpandVBBoxOne.name], self.config.dst_image_path, self.config.dst_mask_path)
        self.plugins_stack.append(mySaveVBBoxNifty)

    def run(self):
        print("Running iothVBBoxPerNodulePipeline...")
        continueProcessing = True

        start_time = time.process_time()  # process_time does not include time elapsed during sleep.

        while continueProcessing:
            continueProcessing = super().execute_stack()
            print("--------------------------------------------------------------------")

        elapsed_time = time.process_time() - start_time  # it measures in seconds
        elapsed_time /= 60  # to minutes
        print("Elapsed time for the FeatureExtractionProcessing: {:.2f} minutes.".format(elapsed_time))


def debug_test():
    from configuration import Configuration

    #config = Configuration("config/conf_ioth_vbboxPerNodule.py", "extract features").load()
    config = Configuration("config/conf_part1.py", "extract features").load()

    my_iothVBBoxPerNoduleProcessing = iothVBBoxPerNodulePipeline('iothVBBoxPerNodulePipeline', config)
    my_iothVBBoxPerNoduleProcessing.build_stack()
    my_iothVBBoxPerNoduleProcessing.run()

if __name__ == '__main__':
    debug_test()



