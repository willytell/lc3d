import os
from importlib.machinery import SourceFileLoader

class Configuration():
    def __init__(self, config_file, action):
        self.config_file = config_file      # path + config file
        self.action = action

    def load(self):
        # load experiment config file
        config = SourceFileLoader('config', self.config_file).load_module()

        # Train the cnn
        if self.action == 'voi+':
            print("Action is voi+...")

            #config.output_path = os.path.join(config.experiments_path, config.experiment_name, config.model_output_directory)

            #if not os.path.exists(config.output_path):
            #    os.makedirs(config.output_path)


        return config