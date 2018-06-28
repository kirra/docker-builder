import json
import logging
import os
import re
import subprocess
from contextlib import contextmanager


@contextmanager
def working_dir(directory):
    prev_cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev_cwd)


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

    def run_pre_build_scripts(self):
        if 'pre_build' not in self.metadata:
            return

        logging.debug("Running pre build scripts for {}".format(self.name))

        with working_dir(self.dir_name):
            for line in self.metadata['pre_build']:
                process = subprocess.Popen(line.split())
                process.wait()

    def build(self):
        logging.debug("Building {}".format(self.name))

        with working_dir(self.dir_name):
            arguments = ''

            if 'arguments' in self.metadata:
                argument_items = self.metadata['arguments'].items()
                arguments = ' '.join("{:s} {:s}".format(key, val) for (key, val) in argument_items)

            command = "docker build {:s} -t {:s} .".format(arguments.strip(), self.name)

            process = subprocess.Popen(command.split())
            process.wait()
