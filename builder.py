import logging

from lib.builder import Builder

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    builder = Builder()
    builder.run()
