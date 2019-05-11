# Todo: This test should be rewritten so only the builder is tested!
import unittest
from configparser import ConfigParser
from typing import Dict, List

from builder.builder import Builder
from builder.config import Config
from builder.dependency import ResolverException
from builder.image import Image


@unittest.skip
class BuilderTest(unittest.TestCase):
    @staticmethod
    def get_config(config: Dict):
        base_config = {'core': {'push': False}, 'logging': {'level': 'debug'}}

        return {**base_config, **config}

    def test_index_images(self) -> None:
        """
        Todo: Implement this test.
        :return:
        """
        config = BuilderTest.get_config({'directories': ['/tmp/containers']})
        builder = Builder(config)

        builder.index_images()


@unittest.skip
class BuilderTestSkip(unittest.TestCase):

    @staticmethod
    def create_builder():
        config_parser = ConfigParser()
        config = Config(config_parser, {})
        builder = Builder(config.config)
        return builder

    @staticmethod
    def create_image(name: str, dependencies: list, images: dict):
        image = Image('/tmp/' + name)
        image.name = name
        image.dependencies = dependencies
        images[name] = image

    def create_simple_dependencies(self) -> Dict[str, Image]:
        images = {}

        #   d       h
        #  / \     / \
        # b   c   i   g
        #      \
        #       a
        #      / \
        #     e   f
        #

        self.create_image('d', [], images)
        self.create_image('a', ['c'], images)
        self.create_image('b', ['d', 'remote1'], images)
        self.create_image('c', ['d', 'remote2'], images)
        self.create_image('e', ['a'], images)
        self.create_image('f', ['a'], images)

        self.create_image('h', [], images)
        self.create_image('i', ['h'], images)
        self.create_image('g', ['h'], images)

        return images

    def check_graph_order(self, target: str, before: List[str], order: List[str]):

        check_list = {key: False for key in before}
        check_list[target] = False

        for check in check_list:
            self.assertTrue(check in order)

        for node in order:
            check_list[node] = True

            if check_list[target]:
                bla = [check_list[check] for check in before]
                self.assertEqual(sum(bla), 0)
                break

    def test_resolve_dependencies_simple(self) -> None:

        builder = self.create_builder()
        images = self.create_simple_dependencies()

        builder.images = images
        builder.build_dependency_graph()
        builder.resolve_dependencies()

        # All the images should be present.
        self.assertTrue(len(builder.local_dependencies), 7)

        # The two remote dependencies should be there.
        self.assertTrue('remote1' in builder.remote_dependencies)
        self.assertTrue('remote2' in builder.remote_dependencies)

        # Do some checks on the order of the dependencies.
        self.check_graph_order('c', ['a', 'e', 'f'], builder.local_dependencies)
        self.check_graph_order('a', ['e', 'f'], builder.local_dependencies)

    def test_resolve_dependencies_circular(self) -> None:

        builder = self.create_builder()

        images = {}
        self.create_image('a', ['b'], images)
        self.create_image('b', ['c'], images)
        self.create_image('c', ['a'], images)

        #   a
        #  / \
        # c - b

        builder.images = images
        builder.build_dependency_graph()

        # There is a circular dependency, therefor we expect a ResolverException.
        with self.assertRaises(ResolverException):
            builder.resolve_dependencies()

    def test_resolve_dependency(self) -> None:

        builder = self.create_builder()
        images = self.create_simple_dependencies()

        builder.images = images
        builder.build_dependency_graph()

        # Get the order for image 'c'.
        builder.resolve_dependency('c')

        # 'b' should no longer be present.
        self.assertTrue(len(builder.local_dependencies), 6)
        self.assertTrue('b' not in builder.local_dependencies)

        self.assertTrue('remote1' not in builder.remote_dependencies)
        self.assertTrue('remote2' in builder.remote_dependencies)

        self.check_graph_order('d', ['c'], builder.local_dependencies)
