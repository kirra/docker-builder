from configparser import ConfigParser
import logging


class Config:
    def __init__(self, file: ConfigParser, args: dict):

        self.file = file
        self.arguments = args
        self.config = {}

        self._merge_config()

        logging.debug("Initialized config: {:s}.".format(str(self.config)))

    def _merge_config(self) -> None:
        """
        Merges the file config and the CLI arguments. CLI arguments always take precedence over file
        config.
        :return: None.
        """

        config = self._parse_file_config()

        if self.arguments.get('push') is True:
            config['core']['push'] = self.arguments['push']

        if self.arguments.get('no_push') is False:
            config['core']['push'] = self.arguments['no_push']

        if 'downstream' in self.arguments:
            config['core']['downstream'] = self.arguments['downstream']

        if 'logging_level' in self.arguments:
            config['logging']['level'] = self.arguments['logging_level']

        if self.arguments.get('dir') is not None:
            config['directories'] = self.arguments['dir']

        if self.arguments.get('registry') is not None:
            config['registries'] = self.arguments['registry']

        if self.arguments.get('images') is not None:
            config['images'] = self.arguments['images']

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
            'directories': [],
            'images': [],
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

