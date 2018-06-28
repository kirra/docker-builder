import glob
import logging
import subprocess
import sys

from lib.dependency import Node, Resolver
from lib.image import Image


class Builder:

    def __init__(self):

        self.images = {}
        self.local_dependencies = []
        self.external_dependencies = []

    def run(self):
        self.read_manifest()
        self.index_images()
        self.resolve_dependencies()
        self.pull_images()
        self.build_images()

    def index_images(self) -> None:
        """ Index the Images found in the current directory. """

        for dockerfile in glob.glob('containers/*/Dockerfile'):
            image = Image(dockerfile)
            image.index()
            self.images[image.name] = image

    def resolve_dependencies(self) -> None:
        """ Resolve the dependencies of the indexed Images. """

        nodes = {image.name: Node(image.name) for image in self.images.values()}

        for image in self.images.values():

            for dep in image.dependencies:

                if dep in self.images:
                    nodes[image.name].add_edge(nodes[dep])

                elif dep not in self.external_dependencies:
                    self.external_dependencies.append(dep)

        resolver = Resolver(nodes.values())
        dependencies = resolver.resolve_dependencies()

        self.local_dependencies = dependencies

        logging.debug("External dependencies found: {:s}".format(str(self.external_dependencies)))

    def build_images(self):
        """ Build the indexed local Images in order of dependencies, lowest number of dependencies
        first. """

        for dep in self.local_dependencies:
            self.images[dep.name].build()

    def read_manifest(self):
        #self.manifest = json.load(open(manifest, 'r'))
        pass

    def pull_images(self):
        """ Pull external dependencies. """

        for image in self.external_dependencies:
            logging.debug("Pulling image {:s}".format(image))

            command = "docker pull {:s}".format(image).split(" ")
            process = subprocess.Popen(command)
            process.wait()


