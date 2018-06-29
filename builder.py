import argparse
import logging
import os

from lib.builder import Builder

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Docker builder, to build docker images with up- and/or downstream dependencies"
    )

    parser.add_argument('-i', '--image', help="Name of the image to build")
    parser.add_argument('-d', '--dir', action='append', default=os.getcwd(),
                        help="The directory to scan for Dockerfiles, multiple directories can be given, if none are given the current directory is used.")
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Logging set to debug")
    else:
        logging.basicConfig(level=logging.WARNING)

    print(args.dir)



    #builder = Builder()
    #builder.run()
