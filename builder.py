import argparse
import configparser
import logging
import os

from builder.builder import Builder
from builder.config import Config


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Docker builder, to build Docker images with up- and/or downstream dependencies"
    )

    # Todo: Fix this so that push is enabled by default
    parser.add_argument('-p', '--push', action='store_true', default=True,
                        help="Push the image(s) to the registry after building")
    parser.add_argument('-r', '--registry', action='append', help="The registries to push the images to")
    parser.add_argument('-i', '--image', action='append', dest='images', help="Name of an image to build")
    parser.add_argument('-d', '--dir', action='append',
                        help="The directory to scan for Dockerfiles, multiple directories can be given, if none are given the current directory is used.")
    parser.add_argument('--downstream', action="store_true", help="Only build the downstream dependencies when an --image is given")
    parser.add_argument('-v', '--verbose', action='store_true')

    # Parse CLI arguments
    args = parser.parse_args()
    arguments = vars(args)

    if arguments['dir'] is None:
        arguments['dir'] = [os.getcwd()]

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Logging set to debug")
        arguments['logging_level'] = 'debug'
    else:
        logging.basicConfig(level=logging.WARNING)
        arguments['logging_level'] = 'warning'

    # Parse config file
    file = configparser.ConfigParser(allow_no_value=True)
    config_file = os.environ['HOME'] + '/.Dockerbuild'
    if os.path.exists(config_file):
        file.read(config_file)

    config = Config(file, arguments)

    builder = Builder(config.config)
    builder.run()
