from configparser import ConfigParser
import logging
from typing import Union


class Config:
    def __init__(self, file: ConfigParser, args: dict):

        self.file = file
        self.arguments = args
        self.config = {}

        self._merge_config()

        logging.debug("Initialized config: {:s}.".format(str(self.config)))


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

    def _merge_config(self) -> None:
        """
        Merges the file config and the CLI arguments. CLI arguments always take precedence over file config.
        :return: None.
        """

        config = self._parse_file_config()
        if 'push' in self.arguments:
            config['core']['push'] = self.arguments['push']

        if 'logging_level' in self.arguments:
            config['logging']['level'] = self.arguments['logging_level']

        if self.arguments.get('dir') is not None:
            config['directories'] = self.arguments['dir']

        if self.arguments.get('registry') is not None:
            config['registries'] = self.arguments['registry']

        self.config = config

    def _parse_file_config(self) -> dict:
        """
        Parses a file config and returns a dict with a default config.
        :return: Dict with the correct values per config section.
        """

        config = {
            'core': {},
            'logging': {},
            'registries': [],
            'directories': []
        }

        if 'core' in self.file:
            section = self.file['core']

            if 'push' in section:
                config['core']['push'] = section.getboolean('push')

            logging.debug("Parsed file config for <{:s}>: {:s}".format('core', str(config['core'])))

        if 'logging' in self.file:
            section = self.file['logging']

            if 'level' in section:
                config['logging']['level'] = section['level']

            logging.debug("Parsed file config for <{:s}>: {:s}".format('logging', str(config['logging'])))

        if 'registries' in self.file:
            section = self.file['registries']

            for registry in section:
                config['registries'].append(registry)

            logging.debug("Parsed file config for <{:s}>: {:s}".format('registries', str(config['registries'])))

        if 'directories' in self.file:
            section = self.file['directories']

            for directory in section:
                config['directories'].append(directory)

            logging.debug("Parsed file config for <{:s}>: {:s}".format('directories', str(config['directories'])))

        logging.debug("Parsed file config: {:s}".format(str(config)))

        return config

