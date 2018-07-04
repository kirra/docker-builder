import glob
import logging
import subprocess
from typing import List

from lib.dependency import Node, Resolver, Graph, NodeList
from lib.image import Image


class Builder:

    def __init__(self, config: dict):
        self.config = config

        self.images = {}
        self.graph = None

        self.local_dependencies = []
        self.remote_dependencies = []

    def run(self):
        """ Runs methods to build all images. """
        self.index_images()

        self.resolve_dependencies()

        if len(self.config['images']) > 0:
            if self.config['core']['downstream']:
                self.filter_dependencies_downstream(self.config['images'])
            else:
                self.filter_dependencies(self.config['images'])

        self.pull_images()
        self.build_images()

        if self.config['core']['push']:
            self.push_images()

    def index_images(self) -> None:
        """
        Index the images found in the current directory and build their dependency graph.
        """

        for directory in self.config['directories']:
            logging.debug("Indexing images for directory {:s}".format(directory))

            for dockerfile in glob.glob("{:s}/*/Dockerfile".format(directory)):
                image = Image(dockerfile)
                image.index()
                self.images[image.name] = image

        logging.debug("Building dependency graph")

        self._build_dependency_graph()

    def resolve_dependencies(self) -> None:
        """
        Resolve the dependencies of all indexed images.
        :return: None.
        """

        logging.debug('Resolving dependency order (all)')

        self._split_dependencies(Resolver(list(self.graph.nodes.values())).resolve_dependencies())

        logging.debug("Dependency order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Dependency order (remote): {:s}".format(str(self.remote_dependencies)))

    def resolve_dependency(self, name: str) -> None:
        """
        Resolve dependencies for a single indexed image and return them.
        :param name: The name of the image to resolve the dependencies for.
        :return:
        """

        logging.debug("Resolving dependency order ({:s})".format(name))

        self._split_dependencies(Resolver([self.graph.local_nodes[name]]).resolve_dependencies())

        logging.debug("Dependency order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Dependency order (remote): {:s}".format(str(self.remote_dependencies)))

    def _build_dependency_graph(self) -> None:
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

        self.graph = graph

    def _split_dependencies(self, dependencies: NodeList) -> None:
        """
        Split dependencies into local and remote dependencies.
        :param dependencies:
        :return:
        """

        for dependency in dependencies:

            if dependency.name in self.graph.local_nodes and dependency.name not in self.local_dependencies:
                self.local_dependencies.append(dependency.name)

            elif dependency.name in self.graph.remote_nodes and dependency.name not in self.remote_dependencies:
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

    def push_images(self):
        """ Push the images to the registries. """

        for dependency in self.local_dependencies:
            for registry in self.config['registries']:
                self.images[dependency].push(registry)

    def filter_dependencies_downstream(self, images: List[str]) -> None:
        """
        Filters the dependency order downstream for a list of images.
        :param images: A list of images to resolve the downstream dependencies for.
        :return: None.
        """

        local_dependencies = images

        index = min([self.local_dependencies.index(i) for i in images])

        for dependency in self.local_dependencies[index:]:
            image = self.images[dependency]

            for image_dependency in image.dependencies:
                if image_dependency in local_dependencies:
                    local_dependencies.append(image.name)
                    break

        self.local_dependencies = local_dependencies
        self.remote_dependencies = []

        logging.debug("Filtered downstream order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Filtered downstream order (remote): {:s}".format(str(self.remote_dependencies)))

    def filter_dependencies(self, images: List[str]) -> None:
        """
        Filters the dependency order for a list of images.
        :param images: A list of images to resolve the dependency order for.
        :return: None.
        """

        for image in images:
            self.resolve_dependency(image)

        local_dependencies = self.local_dependencies
        remote_dependencies = self.remote_dependencies

        self.filter_dependencies_downstream(images)

        downstream_local_dependencies = self.local_dependencies
        for dependency in downstream_local_dependencies:
            if dependency not in local_dependencies:
                local_dependencies.append(dependency)

        self.local_dependencies = local_dependencies
        self.remote_dependencies = remote_dependencies

        logging.debug("Filtered order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Filtered order (remote): {:s}".format(str(self.remote_dependencies)))
