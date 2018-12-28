import sys
import time
from abc import ABC, abstractmethod
from input import NiftiManagementPlugin
from utils import get_components
from plugin import LabelPlugin, VolumeBBoxPlugin, ExpandVBBoxPlugin, SaveVBBoxNiftiPlugin, SlidingWindowPlugin, SaveFeaturesPlugin
from expansionStrategy import UniformExpansion, Bg_pExpansion
from slidingwindow import SlidingWindow
from featureExtractionStrategy import RadiomicClass, RadiomicParallelClass


class Pipeline(ABC):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.show_plugin_time = True
        self.show_total_time = True
        self.plugins_stack = []
        self.data = {}
        super().__init__()

    @abstractmethod
    def run (self):
        pass

    def execute_stack(self):
        total_time = 0

        idx = 0
        continueProcessing = True

        while idx != len(self.plugins_stack) and continueProcessing:
            plugin = self.plugins_stack[idx]
            start_time = time.process_time()  # process_time does not include time elapsed during sleep.
            continueProcessing = plugin.process(self.data)
            elapsed_time = time.process_time() - start_time  # it measures in seconds
            #elapsed_time *= 1000  # to milliseconds
            if self.show_plugin_time:
                print("  Elapsed time for the plugin '{}': {:.2f} seconds.".format(plugin.name, elapsed_time))
            total_time += elapsed_time
            idx += 1

        if self.show_total_time:
            print("--------------------------------------------------------------------")
            print("Elapsed time for the plugins stack: {:.2f} seconds.".format(total_time))

        return continueProcessing


class VBBoxPerNodulePipeline(Pipeline):
    def __init__(self, name, config):
        super().__init__(name, config)

    def build_stack(self):
        # Plugin NiftiManagement
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

        # Plugin ExpandVBBoxPlugin: instance num. 1
        myUniformExpansion = UniformExpansion('UniformExpansion', self.config.uniform_nvoxels, self.config.uniform_limit)
        myExpandVBBoxOne = ExpandVBBoxPlugin('CT_mask_vbbox_uniform_expansion', [myLabeling.name, myVolumeBBox.name], myUniformExpansion)
        self.plugins_stack.append(myExpandVBBoxOne)


        # Plugin ExpandVBBoxPlugin: instance num. 2
        myBg_pExpansion = Bg_pExpansion('Bg_pExpansion', self.config.background_p, self.config.groundtruth_p, self.config.bg_p_nvoxels,
                                             self.config.check_bg_percentage)
        myExpandVBBoxTwo = ExpandVBBoxPlugin('CT_mask_vbbox_Bg_p_expansion', [myLabeling.name, myExpandVBBoxOne.name], myBg_pExpansion)
        self.plugins_stack.append(myExpandVBBoxTwo)

        # Plugin SaveVBBoxNifti
        mySaveVBBoxNifti = SaveVBBoxNiftiPlugin('SaveVBBoxNifti',
                                                [myNiftiManagement.name, myExpandVBBoxTwo.name],
                                                self.config.dst_image_path,
                                                self.config.dst_mask_path,
                                                internal = self.config.internal_input)
        self.plugins_stack.append(mySaveVBBoxNifti)

    def run(self):
        print("Running VBBoxPerNoduleProcessing...")
        continueProcessing = True

        start_time = time.process_time()  # process_time does not include time elapsed during sleep.

        while continueProcessing:
            continueProcessing = super().execute_stack()
            print("--------------------------------------------------------------------")

        elapsed_time = time.process_time() - start_time  # it measures in seconds
        elapsed_time /= 60  # to minutes
        print("Elapsed time for the FeatureExtractionProcessing: {:.2f} minutes.".format(elapsed_time))


class FeatureExtractionPipeline(Pipeline):
    def __init__(self, name, config):
        super().__init__(name, config)

    def build_stack(self):
        # Plugin NiftiManagement
        myNiftiManagementPlugin = NiftiManagementPlugin('CT',
                                                  None,
                                                  self.config.src_image_path,
                                                  self.config.src_mask_path,
                                                  self.config.mask_pattern,
                                                  self.config.dst_image_path,
                                                  self.config.dst_mask_path,
                                                  internal=self.config.internal_input)
        myNiftiManagementPlugin.masks2read()
        self.plugins_stack.append(myNiftiManagementPlugin)

        # Plugin SlidingWindowPlugin
        winSize = self.config.window_size
        mySlidingWindow = SlidingWindow(window_size=winSize, mode=self.config.mode,
                                        window=(winSize, winSize, winSize),
                                        asteps=(self.config.deltaZ, self.config.deltaX, self.config.deltaY), # asteps = (z,x,y)
                                        wsteps=None,
                                        axes=None,
                                        toend=True)

        myRadiomic = RadiomicParallelClass('Radiomic')

        myRadiomic.build_mask_trick(self.config.window_size)
        myRadiomic.build_extractor(self.config.radiomicConfigFile)

        mySlidingWindowPlugin = SlidingWindowPlugin('SlidingWindowPlugin',
                                                    [myNiftiManagementPlugin.name],
                                                    slidingWindow=mySlidingWindow,
                                                    strategy=myRadiomic)
        self.plugins_stack.append(mySlidingWindowPlugin)

        # Plugin SaveFeaturesPlugin
        mySaveFeaturesPluginCSV = SaveFeaturesPlugin('SaveFeaturesCSV',
                                                     [myNiftiManagementPlugin.name, mySlidingWindowPlugin.name],
                                                     self.config.radiomicOutputPath,
                                                     'csv',  # self.config.radiomicOutputFormat
                                                     ';',  # self.config.sep,
                                                     'utf-8')  # self.config.encoding
        self.plugins_stack.append(mySaveFeaturesPluginCSV)


        # Plugin SaveFeaturesPlugin
        mySaveFeaturesPluginXLS = SaveFeaturesPlugin('SaveFeaturesXLSX',
                                                  [myNiftiManagementPlugin.name, mySlidingWindowPlugin.name],
                                                  self.config.radiomicOutputPath,
                                                  'xlsx', #self.config.radiomicOutputFormat
                                                  None, #self.config.sep,
                                                  None) #self.config.encoding
        self.plugins_stack.append(mySaveFeaturesPluginXLS)

        # Plugin SaveFeaturesPlugin
        mySaveFeaturesPluginNPZ = SaveFeaturesPlugin('SaveFeaturesNPZ',
                                                  [myNiftiManagementPlugin.name, mySlidingWindowPlugin.name],
                                                  self.config.radiomicOutputPath,
                                                  'npz',  # 'xls', #self.config.radiomicOutputFormat
                                                  None,  # self.config.sep,
                                                  None)  # self.config.encoding
        self.plugins_stack.append(mySaveFeaturesPluginNPZ)

        # Plugin SaveFeaturesPlugin
        mySaveFeaturesPluginMATLAB = SaveFeaturesPlugin('SaveFeaturesMATLAB',
                                                     [myNiftiManagementPlugin.name, mySlidingWindowPlugin.name],
                                                     self.config.radiomicOutputPath,
                                                     'mat',  # 'xls', #self.config.radiomicOutputFormat
                                                     None,  # self.config.sep,
                                                     None)  # self.config.encoding
        self.plugins_stack.append(mySaveFeaturesPluginMATLAB)


    def run(self):
        print("Running FeatureExtractionProcessing...")
        continueProcessing = True

        start_time = time.process_time()  # process_time does not include time elapsed during sleep.

        while continueProcessing:
            continueProcessing = super().execute_stack()
            print("--------------------------------------------------------------------")

        elapsed_time = time.process_time() - start_time  # it measures in seconds
        elapsed_time /= 60  # to minutes
        print("Elapsed time for the FeatureExtractionProcessing: {:.2f} minutes.".format(elapsed_time))


# def debug_test():
#     from configuration import Configuration
#
#     config = Configuration("config/conf_part3.py", "ROI").load()
#
#     myVBBoxPerNoduleProcessing = VBBoxPerNodulePipeline('VBBoxPerNodulePipeline', config)
#     myVBBoxPerNoduleProcessing.build_stack()
#     myVBBoxPerNoduleProcessing.run()

def debug_test():
    from configuration import Configuration

    config = Configuration("config/conf_part4.py", "extract features").load()

    myFeatureExtractionPipeline = FeatureExtractionPipeline('FeatureExtractionProcessing', config)
    myFeatureExtractionPipeline.build_stack()
    myFeatureExtractionPipeline.run()


if __name__ == '__main__':
    debug_test()



