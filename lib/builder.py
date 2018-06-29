import glob
import logging
import subprocess

from lib.dependency import Node, Resolver, Graph, NodeList
from lib.image import Image


class Builder:

    def __init__(self):

        self.images = {}
        self.graph = None

        self.local_dependencies = []
        self.remote_dependencies = []

    def run(self):
        """ Runs methods to build all images. """
        self.index_images()

        logging.debug("\nResolving all images\n")
        self.resolve_dependencies()
        self.pull_images()

        logging.debug("\nResolving single image\n")
        self.resolve_dependency('kirra-php:7.1')
        self.pull_images()

        self.build_images()

    def index_images(self) -> None:
        """
        Index the images found in the current directory and build their dependency graph.
        """

        for dockerfile in glob.glob('containers/*/Dockerfile'):
            image = Image(dockerfile)
            image.index()
            self.images[image.name] = image

        self.graph = self._build_dependency_graph()

    def resolve_dependencies(self) -> None:
        """
        Resolve the dependencies of all indexed images.
        :return: None.
        """

        self._build_dependencies(Resolver(self.graph.nodes.values()).resolve_dependencies())

        logging.debug("Dependency order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Dependency order (remote): {:s}".format(str(self.remote_dependencies)))

    def resolve_dependency(self, name: str) -> None:
        """
        Resolve dependencies for a single indexed image and return them.
        :param name: The name of the image to resolve the dependencies for.
        :return:
        """

        self._build_dependencies(Resolver([self.graph.local_nodes[name]]).resolve_dependencies())

        logging.debug("Dependency order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Dependency order (remote): {:s}".format(str(self.remote_dependencies)))

    def _build_dependency_graph(self) -> Graph:
        """
        Builds a dependency graph for the images. Starts by creating a node for every image and
        dependency and then adding the edges.
        :return: An initialized dependency graph.
        """

        images = self.images.values()

        graph = Graph()
        for image in images:
            graph.add_local(Node(image.name))

            for dependency in image.dependencies:
                if dependency not in graph.nodes:
                    if dependency in self.images:
                        graph.add_local(Node(dependency))
                    else:
                        graph.add_remote(Node(dependency))

        for image in images:
            for dependency in image.dependencies:
                graph.nodes[image.name].add_edge(graph.nodes[dependency])

        logging.debug("Dependency graph (local nodes): {:s}".format(str(list(graph.local_nodes.keys()))))
        logging.debug("Dependency graph (remote nodes): {:s}".format(str(list(graph.remote_nodes.keys()))))

        return graph

    def _build_dependencies(self, dependencies: NodeList) -> None:
        """
        Builds ordered dependencies for both local and remote dependency nodes.
        :param dependencies:
        :return:
        """

        self.local_dependencies = []
        self.remote_dependencies = []

        for dependency in dependencies:
            if dependency.name in self.graph.local_nodes:
                self.local_dependencies.append(dependency.name)
            else:
                self.remote_dependencies.append(dependency.name)

    def build_images(self):
        """ Build the indexed local Images in order of dependencies, lowest number of dependencies
        first. """

        for dependency in self.local_dependencies:
            self.images[dependency].build()

    def pull_images(self):
        """ Pull remote dependencies. """

        for image in self.remote_dependencies:
            logging.debug("Pulling image {:s}".format(image))

            command = "docker pull {:s}".format(image).split(" ")
            process = subprocess.Popen(command)
            process.wait()
