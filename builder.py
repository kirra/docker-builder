from lib.node import Node






a = Node('a')
b = Node('b')
c = Node('c')
d = Node('d')
e = Node('e')

a.add_edge(b)
a.add_edge(d)
b.add_edge(c)
b.add_edge(e)
c.add_edge(d)
c.add_edge(e)


def resolve_dependencies(dependency, resolved, unresolved):
    print(dependency.name)
    unresolved.append(dependency)
    for edge in dependency.edges:
        if edge not in resolved:
            if edge in unresolved:
                raise Exception('Circular reference detected: %s -&gt; %s'.format(node.name, edge.name))
            resolve_dependencies(edge, resolved, unresolved)
    resolved.append(dependency)
    unresolved.remove(dependency)


if __name__ == '__main__':
    resolved = []
    resolve_dependencies(a, resolved, [])
    for node in resolved:
        print(node.name)
