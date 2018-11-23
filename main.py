import argparse

from configuration import Configuration
from input import NiftyFormat

def main ():
    parser = argparse.ArgumentParser(description='lc3d')
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument('-v', "--verbose", action="store_true")
    #group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument('-c', '--config_file', type=str, default=None, help='Configuration file')
    parser.add_argument('-a', '--action', type=str, default=None, help='extract features')

    args = parser.parse_args()

    conf = Configuration(args.config_file, args.action).load()

    #if args.verbose:
    #    print("verbose...")
    #elif args.quite:
    #    print("quite...")

    if args.action == 'extract_features':
        print ("Extracting features...")

    n = NiftyFormat("", "", "", "")
    n.get_next()


if __name__ == '__main__':
    main()