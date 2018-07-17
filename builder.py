import argparse
import configparser
import logging
import os

from builder.builder import Builder
from builder.config import Config

def setup_logger(logger):
    sh = logging.StreamHandler()

    def decorate_emit(fn):
        def new(*args):
            levelno = args[0].levelno
            if(levelno >= logging.CRITICAL):
                color = '\x1b[31;1m'
            elif(levelno >= logging.ERROR):
                color = '\x1b[31;1m'
            elif(levelno >= logging.WARNING):
                color = '\x1b[33;1m'
            elif(levelno >= logging.INFO):
                color = '\x1b[32;1m'
            elif(levelno >= logging.DEBUG):
                color = '\x1b[35;1m'
            else:
                color = '\x1b[0m'

            # add colored log level in the beginning of the message
            args[0].msg = "{:s}{:s}:\x1b[0m {:s}".format(color, args[0].levelname, args[0].msg)

            return fn(*args)

        return new

    sh.emit = decorate_emit(sh.emit)

    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(sh)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Docker builder, to build Docker images with up- and/or downstream dependencies"
    )

    push_group = parser.add_mutually_exclusive_group()
    push_group.add_argument('-p', '--push', action='store_true',
                        help="Push the image(s) to the registry after building")
    push_group.add_argument('--no-push', action='store_false',
                        help="Don't push the image(s) to the registry after building")

    parser.add_argument('-r', '--registry', action='append', help="The registries to push the images to")
    parser.add_argument('-i', '--image', action='append', dest='images', help="Name of an image to build")
    parser.add_argument('-d', '--dir', action='append',
                        help="The directory to scan for Dockerfiles, multiple directories can be given.")
    parser.add_argument('--downstream', action="store_true", help="Only build the downstream dependencies when an --image is given")
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--no-color', action='store_true')

    # Parse CLI arguments
    args = parser.parse_args()
    arguments = vars(args)

    # Setup logger
    logging.basicConfig(format='%(levelname)s: %(message)s')
    logger = logging.getLogger()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.debug("Logging set to debug")
        arguments['logging_level'] = 'debug'
    else:
        logger.setLevel(logging.INFO)
        arguments['logging_level'] = 'info'

    if not args.no_color:
        setup_logger(logger)

    # Parse config file
    file = configparser.ConfigParser(allow_no_value=True)
    config_file = os.environ['HOME'] + '/.Dockerbuild'
    if os.path.exists(config_file):
        file.read(config_file)

    config = Config(file, arguments)

    builder = Builder(config.config)
    builder.run()
