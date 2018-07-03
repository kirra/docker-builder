from configparser import ConfigParser
from unittest import TestCase

from lib.builder import Builder
from lib.config import Config
from lib.dependency import ResolverException
from lib.image import Image


class BuilderTest(TestCase):

    def create_builder(self):
        configparser = ConfigParser()
        config = Config(configparser, {})
        builder = Builder(config)
        return builder

    def create_image(self, name, dependencies, images):
        image = Image('/tmp/' + name)
        image.name = name
        image.dependencies = dependencies
        images[name] = image

    def create_simple_dependencies(self):
        images = {}

        #   d      h
        #  / \    / \
        # b   c  i   g
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

    def check_graph_order(self, target, before, order):
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

    def test_filter_dependencies(self):

        builder = self.create_builder()
        images = self.create_simple_dependencies()

        builder.images = images
        builder._build_dependency_graph()
        builder.resolve_dependencies()
        builder.filter_dependencies(['c', 'h'])

        self.check_graph_order('c', ['a', 'e', 'f'], builder.local_dependencies)
        self.check_graph_order('h', ['i', 'g'], builder.local_dependencies)


    def test_resolve_dependencies_simple(self):

        builder = self.create_builder()
        images = self.create_simple_dependencies()

        builder.images = images
        builder._build_dependency_graph()
        builder.resolve_dependencies()

        # All the images should be present.
        self.assertTrue(len(builder.local_dependencies), 7)

        # The two remote dependencies should be there.
        self.assertTrue('remote1' in builder.remote_dependencies)
        self.assertTrue('remote2' in builder.remote_dependencies)

        # Do some checks on the order of the dependencies.
        self.check_graph_order('c', ['a', 'e', 'f'], builder.local_dependencies)
        self.check_graph_order('a', ['e', 'f'], builder.local_dependencies)


    def test_resolve_dependencies_circular(self):

        builder = self.create_builder()

        images = {}
        self.create_image('a', ['b'], images)
        self.create_image('b', ['c'], images)
        self.create_image('c', ['a'], images)

        #   a
        #  / \
        # c - b

        builder.images = images
        builder._build_dependency_graph()

        # There is a circular dependency, therefor we expect a ResolverException.
        with self.assertRaises(ResolverException):
            builder.resolve_dependencies()

    def test_resolve_dependency(self):

        builder = self.create_builder()
        images = self.create_simple_dependencies()

        builder.images = images
        builder._build_dependency_graph()

        # Get the order for image 'c'.
        builder.resolve_dependency('c')

        # 'b' should no longer be present.
        self.assertTrue(len(builder.local_dependencies), 6)
        self.assertTrue('b' not in builder.local_dependencies)

        self.assertTrue('remote1' not in builder.remote_dependencies)
        self.assertTrue('remote2' in builder.remote_dependencies)

        # 'd' is still the root.
        self.assertEqual(builder.local_dependencies[0], 'd')

        self.check_graph_order('c', ['a', 'e', 'f'], builder.local_dependencies)
        self.check_graph_order('a', ['e', 'f'], builder.local_dependencies)
