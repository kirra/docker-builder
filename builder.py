import argparse
import configparser
import logging
import os

from lib.builder import Builder
from lib.config import Config


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Docker builder, to build Docker images with up- and/or downstream dependencies"
    )

    parser.add_argument('-p', '--push', action='store_true', help="Push the image(s) to the registry after building")
    parser.add_argument('-r', '--registry', action='append', help="The registries to push the images to")
    parser.add_argument('-i', '--image', action='append', help="Name of the images to build")
    parser.add_argument('-d', '--dir', action='append',
                        help="The directory to scan for Dockerfiles, multiple directories can be given, if none are given the current directory is used.")
    parser.add_argument('-v', '--verbose', action='store_true')

    # Parse CLI arguments
    args = parser.parse_args()
    arguments = vars(args)

    if arguments['dir'] is None:
        arguments['dir'] = [os.getcwd()]

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Logging set to debug")
    else:
        logging.basicConfig(level=logging.WARNING)

    # Parse config file
    file = {}
    config_file = os.environ['HOME'] + '/.Dockerbuild'
    if os.path.exists(config_file):
        config = configparser.ConfigParser().read(config_file)
        logging.debug(config)


        file = {s: dict(config.items(s)) for s in config.sections()}

    config = Config(file, arguments)

    builder = Builder(config)
    # builder.run()
