import json
import logging
import os
import re


class Image:

    def __init__(self, file_path):
        self.file_path = file_path

        self.dependencies = []
        self.metadata = {}
        self.name = None

        self.dir_name = os.path.dirname(self.file_path)
        self.image_name = self.dir_name

    def index(self):
        self._parse_metadata()
        self._parse_dockerfile()

    def _parse_dockerfile(self):
        with open(self.file_path, 'r') as handle:
            lines = handle.readlines()

        from_pattern = re.compile('^FROM ([^\s]+)')
        copy_pattern = re.compile('--from=(.+?) ')

        for line in lines:

            for match in from_pattern.finditer(line):
                self.dependencies.append(match.group(1))

            for match in copy_pattern.finditer(line):
                self.dependencies.append(match.group(1))

        self.dependencies = list(set(self.dependencies))

        logging.debug("{:s} has dependencies: {:s}".format(self.image_name, str(self.dependencies)))

    def _parse_metadata(self):
        metadata_file = "{}/metadata.json".format(self.dir_name)
        self.metadata = json.load(open(metadata_file, 'r'))
        self.name = self.metadata['local_tag']

    def build(self):
        logging.debug("Building {}".format(self.name))