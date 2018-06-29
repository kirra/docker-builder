import argparse
import logging
import os

from lib.builder import Builder


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Docker builder, to build Docker images with up- and/or downstream dependencies"
    )

    parser.add_argument('-p', '--push', action='store_true', help="Push the image(s) to the registry after building")
    parser.add_argument('-r', '--registry', action='append', help="The registries to push the images to")
    parser.add_argument('-i', '--image', action='append', help="Name of the images to build")
    parser.add_argument('-d', '--dir', action='append', default=os.getcwd(),
                        help="The directory to scan for Dockerfiles, multiple directories can be given, if none are given the current directory is used.")
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Logging set to debug")
    else:
        logging.basicConfig(level=logging.WARNING)

    builder = Builder()
    builder.run()
