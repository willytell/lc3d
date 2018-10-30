#from abc import ABC, abstractmethod
from plugin import Plugin
from configuration import Configuration

class Input(Plugin):
    pass

class LoadNifty(Input):
    def process(self, config, data):
        print("load nifty...")


def test():
    config = Configuration("config/conf_extractfeatures.py", "extract features")

    load = LoadNifty('loadNifty')
    load.process(config, None, None)


if __name__ == '__main__':
    test()