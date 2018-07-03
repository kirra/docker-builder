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
        self.manifest = {}
        self.name = None

        self.dir_name = os.path.dirname(self.file_path)
        self.image_name = self.dir_name

    def index(self) -> None:
        """
        Indexes a Docker image by parsing a manifest and the Dockerfile.
        :return: None.
        """
        self._parse_manifest()
        self._parse_dockerfile()

    def _parse_dockerfile(self) -> None:
        """
        Parses a Dockerfile and stores the dependencies.
        :return: None.
        """
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

        logging.debug("{:s} has dependencies: {:s}".format(self.name, str(self.dependencies)))

    def _parse_manifest(self) -> None:
        """
        Parses a manifest file which holds settings for a Docker image.
        :return: None.
        """

        manifest_file = "{}/manifest.json".format(self.dir_name)

        self.manifest = json.load(open(manifest_file, 'r'))

        self.name = self.image_name
        if 'local_tag' in self.manifest:
            self.name = self.manifest['local_tag']

    def run_pre_build_scripts(self) -> None:
        """
        Runs scripts defined in the manifest's `pre_build` section.
        :return: None.
        """

        if 'pre_build' not in self.manifest:
            return

        logging.debug("Running pre build scripts for {}".format(self.name))

        with working_dir(self.dir_name):
            for line in self.manifest['pre_build']:
                process = subprocess.Popen(line.split())
                process.wait()

    def run_post_build_scripts(self) -> None:
        """
        Runs scripts defined in the manifest's `post_build` section.
        :return: None.
        """

        if 'post_build' not in self.manifest:
            return

        logging.debug("Running post build scripts for {}.".format(self.name))

        with working_dir(self.dir_name):
            for line in self.manifest['post_build']:
                process = subprocess.Popen(line.split())
                process.wait()

    def build(self) -> None:
        """
        Builds a Docker image using the settings in the manifest. If a `local_tag` isn't specified
        in the manifest, the built image isn't tagged.
        :return: None.
        """

        logging.debug("Building {}".format(self.name))

        self.run_pre_build_scripts()

        with working_dir(self.dir_name):
            arguments = {}
            if 'arguments' in self.manifest:
                arguments = self.manifest['arguments']

            if 'local_tag' in self.manifest:
                arguments['-t'] = self.manifest['local_tag']

            cli_arguments = ' '.join("{:s} {:s}".format(option, value) for (option, value) in arguments.items())

            command = "docker build {:s} .".format(cli_arguments.strip(), self.name)
            process = subprocess.Popen(command.split())
            process.wait()

        self.run_post_build_scripts()

    def push(self, registry: str) -> None:
        """
        Pushes a Docker image to a registry defined by `registry` and using the settings in the manifest. If either
        the `local_tag` or the `registry_tag` aren't specified, the image won't be pushed.
        :param str registry: The registry to push the image to.
        :return: None
        """

        if 'local_tag' not in self.manifest or 'registry_tag' not in self.manifest:
            return

        registry_tag = "{:s}/{:s}".format(
            registry.rstrip('/'), self.manifest['registry_tag'].lstrip('/'))

        command = "docker tag {:s} {:s}".format(self.manifest['local_tag'], registry_tag)
        process = subprocess.Popen(command.split())
        process.wait()

        command = "docker push {:s}".format(registry_tag)
        process = subprocess.Popen(command.split())
        process.wait()
