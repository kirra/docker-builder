import glob
import logging
import subprocess

from lib.dependency import Graph, Node, NodeList, Resolver
from lib.image import Image, ImageList


class Builder:

    def __init__(self, config: dict):
        self.config = config

        self.images = {}
        self.graph = None

        self.local_dependencies = []
        self.remote_dependencies = []

    def run(self) -> None:
        """
        Runs methods to build all images.
        """

        # Start by indexing all images
        self.index_images()

        # Either resolve all dependencies or a list of provided images (either full or downstream)
        if len(self.config['images']) > 0:
            images = {image: self.images[image] for image in self.config['images']}
            self.resolve_dependencies(list(images.values()), self.config['core']['downstream'])
        else:
            self.resolve_all_dependencies()

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

        logging.debug('Building dependency graph')

        self._build_dependency_graph()

    def resolve_all_dependencies(self) -> None:
        """
        Resolve the dependencies of all indexed images.
        :return: None.
        """

        logging.debug('Resolving dependency order (all)')

        self._split_dependencies(Resolver(self.graph).resolve())

        logging.debug("Dependency order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Dependency order (remote): {:s}".format(str(self.remote_dependencies)))

    def resolve_dependencies(self, images: ImageList, downstream: bool = False) -> None:
        """
        Resolve dependencies for a single indexed image and return them.
        :param images: A list of images to resolve the dependencies for
        :param bool downstream: If the dependencies should only be resolved downstream.
        """

        logging.debug("Resolving dependency order ({:s}), downstream only: {:s}"
                      .format(str([image.name for image in images]), str(downstream)))

        nodes = {name: self.graph.nodes[name] for name in [image.name for image in images]}

        self._split_dependencies(Resolver(self.graph).resolve_nodes(list(nodes.values()), downstream))

        logging.debug("Dependency order (local): {:s}".format(str(self.local_dependencies)))
        logging.debug("Dependency order (remote): {:s}".format(str(self.remote_dependencies)))

    def _build_dependency_graph(self) -> None:
        """
        Builds a dependency graph for the images. Starts by creating a node for every image and
        dependency and then adding the edges.
        :return: An initialized dependency graph.
        """

        images = self.images.values()
        nodes = {}

        for image in images:
            nodes[image.name] = Node(image.name)

            for dependency in image.dependencies:
                if dependency not in nodes:
                    nodes[dependency] = Node(dependency)

        for image in images:
            for dependency in image.dependencies:
                nodes[image.name].add_edge(nodes[dependency])

        self.graph = Graph.create(list(nodes.values()))

        logging.debug("Dependency graph: {:s}".format(str(list(self.graph.nodes.keys()))))

    def _split_dependencies(self, dependencies: NodeList) -> None:
        """
        Split dependencies into local and remote dependencies.
        :param NodeList dependencies: The dependencies to split.
        """

        for dependency in dependencies:
            if dependency.name in self.images and dependency.name not in self.local_dependencies:
                self.local_dependencies.append(dependency)
            elif dependency.name not in self.images and dependency.name not in self.remote_dependencies:
                self.remote_dependencies.append(dependency)

    def build_images(self) -> None:
        """
        Build the indexed Images in order of dependencies, lowest number of dependencies first.
        """

        for dependency in self.local_dependencies:
            self.images[dependency.name].build()

    def pull_images(self) -> None:
        """
        Pull remote dependencies.
        """

        for dependency in self.remote_dependencies:
            logging.debug("Pulling image {:s}".format(dependency.name))

            command = "docker pull {:s}".format(dependency.name).split(" ")
            process = subprocess.Popen(command)
            process.wait()

    def push_images(self) -> None:
        """
        Push the images to the registries.
        """

        for dependency in self.local_dependencies:
            for registry in self.config['registries']:
                self.images[dependency.name].push(registry)
