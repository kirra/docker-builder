import json
import os
import re


class Image:
    def __init__(self, dockerfile):
        self.dockerfile = dockerfile
        self.dependencies = []
        self.dir_name = os.path.dirname(self.dockerfile)

        self._parse_manifest()
        self._parse_dockerfile()

    def _parse_dockerfile(self):
        with open(self.dockerfile, 'r') as handle:
            lines = handle.readlines()

        from_pattern = re.compile('^FROM ([^\s]+)')
        copy_pattern = re.compile('--from=(.+?) ')

        for line in lines:

            for match in from_pattern.finditer(line):
                self.dependencies.append(match.group(1))

            for match in copy_pattern.finditer(line):
                self.dependencies.append(match.group(1))

    def _parse_manifest(self):
        manifest = "{}/manifest.json".format(self.dir_name)
        self.manifest = json.load(open(manifest, 'r'))
        self.name = self.manifest['local_tag']