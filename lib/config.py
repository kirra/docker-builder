import configparser
import logging
from typing import Union


class Config:
    def __init__(self, file: dict, args: dict):

        self.file = file
        self.arguments = args

        logging.debug('Initialized config')
        logging.debug(self.file)
        logging.debug(self.arguments)


    def _write(self) -> None:
        """
        Writes the config file.
        :return: None
        """
        self.config.write(self.config_file)

    def _read(self, section: str, key: str) -> Union[str, bool, None]:
        """
        Reads the config file.
        :param section: The section to read the key from.
        :param key: The key to get the value for.
        :return:
        """
        if section not in self.config:
            return None
        elif key not in self.config[section]:
            return None

        return self.config[section][key]
