import copy
from typing import List, Dict

NodeList = List['Node']
NodeDict = Dict[str, 'Node']


class Node:
    def __init__(self, name: str):
        self.name = name
        self.edges = []

    def add_edge(self, edge: 'Node') -> None:
        """
        Adds an edge to the node.
        :param Node edge: The edge to add.
        """
        self.edges.append(edge)

    def __repr__(self):
        return self.name


class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node: Node) -> None:
        """
        Adds a node to the graph.
        :param Node node: The node to add.
        """

        if node.name not in self.nodes:
            self.nodes[node.name] = node

    @staticmethod
    def create(nodes: NodeList) -> 'Graph':
        """
        Builds a graph from a list nodes.
        :param NodeList nodes: The nodes to build a graph from.
        :return Graph: The graph.
        """

        graph = Graph()
        for node in nodes:
            graph.add_node(node)

        return graph

    @staticmethod
    def filter(graph: 'Graph', nodes: NodeList, downstream: bool = False) -> 'Graph':
        """
        Creates a new graph by filtering an existing graph so only the nodes and dependent nodes remain.
        :param Graph graph: The graph to filter.
        :param NodeList nodes: The nodes to remain after filtering
        :param bool downstream: If True, only downstream nodes are returned in the filtered graph.
        :return Graph: The filtered graph.
        """

        # Start by searching for downstream nodes, append them to the list
        for node in nodes:
            for candidate in graph.nodes.values():
                if node in candidate.edges:
                    nodes.append(candidate)

        # Return early when only downstream nodes are required, remove edges that aren't in the node list
        if downstream:
            for node in nodes:
                edges = copy.copy(node.edges)
                for edge in edges:
                    if edge not in nodes:
                        node.edges.remove(edge)

            return Graph.create(nodes)

        # Resolve all nodes upstream
        visited_nodes = set()
        while nodes:
            node = nodes.pop(0)
            if node.name not in visited_nodes:
                visited_nodes.add(node.name)

            for edge in node.edges:
                if edge.name not in visited_nodes:
                    nodes.append(edge)
                    visited_nodes.add(edge.name)

        # Create a new graph with the filtered node list
        nodes = {name: graph.nodes[name] for name in visited_nodes}

        return Graph.create(list(nodes.values()))


class ResolverException(Exception):
    pass


class Resolver:
    def __init__(self, graph: Graph):
        self.graph = graph

    def _topological_sort(self) -> List[str]:
        """
        Does a topological sort of a dependency graph.
        :return List[str]: The topological order of the dependency graph.
        """

        result = []
        zero_in_degree = []

        nodes = self.graph.nodes
        in_degree = {node: 0 for node in nodes}

        for node in nodes:
            for edge in nodes[node].edges:
                in_degree[edge.name] += 1

        for d in in_degree:
            if in_degree[d] == 0:
                zero_in_degree.append(d)

        while zero_in_degree:
            n = zero_in_degree.pop(0)
            result.append(n)

            for edge in nodes[n].edges:
                in_degree[edge.name] -= 1
                if in_degree[edge.name] == 0:
                    zero_in_degree.append(edge.name)

        return result

    def resolve(self) -> NodeList:
        """
        Returns the order for a dependency graph.
        :return NodeList: The dependency order.
        """

        order = self._topological_sort()[::-1]
        if len(order) != len(self.graph.nodes):
            cyclic = set(self.graph.nodes.keys()).difference(set(order))
            raise ResolverException("Cyclic dependencies detected in nodes {:s}.".format(str(cyclic)))

        return [self.graph.nodes[name] for name in order]

    def resolve_nodes(self, nodes: NodeList, downstream: bool = False) -> NodeList:
        """
        Returns the order for a single node.
        :param NodeList nodes: A list of nodes to return the dependency order for.
        :param bool downstream: If True, only downstream dependencies are returned.
        :return NodeList: The dependency order.
        """

        original = self.graph
        self.graph = Graph.filter(self.graph, nodes, downstream)

        order = self.resolve()
        self.graph = original

        return order
