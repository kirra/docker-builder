import unittest
from typing import Dict, List

from lib.dependency import Graph, Node, NodeList, Resolver, ResolverException


class DependencyTest(unittest.TestCase):
    @staticmethod
    def create_node(name: str, dependencies: List[str], nodes: Dict[str, Node]) -> None:
        if name not in nodes:
            nodes[name] = Node(name)

        for dependency in dependencies:
            if dependency not in nodes:
                nodes[dependency] = Node(dependency)

            nodes[name].add_edge(nodes[dependency])

    def create_graph(self) -> Graph:
        nodes = {}

        #   d       i
        #  / \     / \
        # b   c   g   h
        #      \
        #       a
        #      / \
        #     e   f

        self.create_node('a', ['c'], nodes)
        self.create_node('b', ['d'], nodes)
        self.create_node('c', ['d'], nodes)
        self.create_node('d', [], nodes)
        self.create_node('e', ['a'], nodes)
        self.create_node('f', ['a'], nodes)

        self.create_node('g', ['i'], nodes)
        self.create_node('h', ['i'], nodes)
        self.create_node('i', [], nodes)

        return Graph.create(list(nodes.values()))

    def assert_dependency_order(self, target: Node, before: NodeList, order: NodeList) -> None:
        checked = {node.name: False for node in before}
        checked[target.name] = False

        ordered = [node.name for node in order]

        for check in checked:
            self.assertTrue(check in ordered)

        for node in ordered:
            checked[node] = True

            if checked[target.name]:
                self.assertEqual(sum([checked[node.name] for node in before]), 0)
                break

    def test_resolve(self) -> None:
        graph = self.create_graph()

        resolver = Resolver(graph)
        order = resolver.resolve()

        # Check order of the dependencies
        self.assert_dependency_order(graph.nodes['a'], [graph.nodes['e'], graph.nodes['f']], order)
        self.assert_dependency_order(graph.nodes['c'], [graph.nodes['a']], order)
        self.assert_dependency_order(graph.nodes['i'], [graph.nodes['h']], order)

    def test_resolve_cyclic(self) -> None:
        nodes = {}

        #   a
        #  / \
        # b - c

        self.create_node('a', ['b'], nodes)
        self.create_node('b', ['c'], nodes)
        self.create_node('c', ['a'], nodes)

        graph = Graph.create(list(nodes.values()))

        resolver = Resolver(graph)

        # There is a circular dependency, therefore we expect a ResolverException
        with self.assertRaises(ResolverException):
            resolver.resolve()

    def test_resolve_node(self) -> None:
        graph = self.create_graph()

        resolver = Resolver(graph)
        order = resolver.resolve_nodes([graph.nodes['a'], graph.nodes['h']])

        # 'b' & 'g' should no longer be present
        self.assertFalse(graph.nodes['b'] in order)
        self.assertFalse(graph.nodes['g'] in order)

        # Check order of the dependencies
        self.assert_dependency_order(graph.nodes['a'], [graph.nodes['e'], graph.nodes['f']], order)
        self.assert_dependency_order(graph.nodes['c'], [graph.nodes['a']], order)
        self.assert_dependency_order(graph.nodes['i'], [graph.nodes['h']], order)

    def test_resolve_node_downstream(self) -> None:
        graph = self.create_graph()

        resolver = Resolver(graph)
        order = resolver.resolve_nodes([graph.nodes['a']], True)

        # 'c', 'd' & 'i' should no longer be present
        self.assertFalse(graph.nodes['c'] in order)
        self.assertFalse(graph.nodes['d'] in order)
        self.assertFalse(graph.nodes['i'] in order)

        # Check order of the dependencies
        self.assert_dependency_order(graph.nodes['a'], [graph.nodes['e'], graph.nodes['f']], order)

    def test_resolve_node_downstream_complex(self) -> None:
        graph = self.create_graph()

        #   d       i
        #  / \     / \
        # b   c   g   h
        #      \
        #   j   a
        #    \ / \
        #     e   f

        nodes = graph.nodes
        self.create_node('j', [], nodes)
        nodes['e'].add_edge(nodes['j'])
        graph = Graph.create(list(nodes.values()))

        resolver = Resolver(graph)
        order = resolver.resolve_nodes([graph.nodes['a']], True)

        # 'c', 'd', 'i' & 'j' should no longer be present
        self.assertFalse(graph.nodes['c'] in order)
        self.assertFalse(graph.nodes['d'] in order)
        self.assertFalse(graph.nodes['i'] in order)

        # Check order of the dependencies
        self.assert_dependency_order(graph.nodes['a'], [graph.nodes['e'], graph.nodes['f']], order)
