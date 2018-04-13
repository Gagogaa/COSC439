"""
Gregory Mann
Project 4
Dijkstra's algorithm
"""

import sys

DEFAULT_OUTFILE = "gmann1_output.txt"
DEFAULT_INFILE = "gmann1_input.txt"


def parse_args(option):
    """Parses the command line arguments for the
    corresponding option or returns None"""
    for i in range(len(sys.argv)):
        if sys.argv[i] == option:
            return sys.argv[i + 1]
    return None


def get_outfile():
    """Get the outfile from the command line or return the default value"""
    result = parse_args("-o")
    return DEFAULT_OUTFILE if result is None else result


def get_infile():
    """Get the infile from the command line or return the default value"""
    result = parse_args("-i")
    return DEFAULT_INFILE if result is None else result


class Edge:
    """A class representing edges of a node"""

    # Init is kinda like a java constructor
    def __init__(self, node, weight):
        self.node = node
        self.weight = weight


class Node:
    """A class representing a network node"""

    def __init__(self, name):
        """Init is kinda like a java constructor"""
        self.name = name
        self.edges = []

    def __str__(self):
        """__str__ is kinda like toString in java"""
        res = f'{self.name} ('

        for edge in self.edges:
            res += f' {edge.node.name}:{edge.weight}'

        res += ' )'

        return res

    # Here I override the >, ==, and hashcode methods used for comparison in python
    def __eq__(self, other):
        return self.name == other.name

    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return self.name.__hash__()


def min_node(nodes, dist):
    """Finds the node with the minimum distance in a set."""
    min_weight = float("inf")
    min_node = None

    for (node, weight) in dist.items():
        if (weight < min_weight) and (node in nodes):
            min_node = node
            min_weight = weight

    return min_node


def get_dist(source, target):
    """Computes the distance from the source to the target returning
     the connected node the source must travel though"""
    node = None
    dist = float("inf")

    for edge in source.edges:
        if target is edge.node:
            dist = edge.weight
            node = target

    return node, dist


def dijkstra(graph, source):
    """Takes a graph and a source node and computes the routes.
    the algorithm is taken from https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm"""

    unvisited = []
    dist = {}
    prev = {}

    for node in graph:
        prev[node], dist[node] = get_dist(source, node)
        unvisited.append(node)

    dist[source] = 0

    while len(unvisited) is not 0:
        u = min_node(unvisited, dist)

        unvisited.remove(u)

        for edge in u.edges:
            alt = dist[u] + edge.weight

            if alt < dist[edge.node]:
                dist[edge.node] = alt
                if u in [x.node for x in source.edges]:
                    prev[edge.node] = u

    return dist, prev


def get_graph():
    """Reads the infile returning the nodes as a list"""

    nodes = {}

    fin = open(get_infile(), "r")

    for line in fin:
        temp = [x.strip() for x in line.split(" ") if x.strip() is not ""]

        n1 = temp[0]
        n2 = temp[1]
        weight = int(temp[2])

        if nodes.get(n1) is None:
            nodes[n1] = Node(n1)
        if nodes.get(n2) is None:
            nodes[n2] = Node(n2)

        nodes[n1].edges.append(Edge(nodes[n2], weight))
        nodes[n2].edges.append(Edge(nodes[n1], weight))

    fin.close()

    ret = [x for x in nodes.values()]

    ret.sort()

    return ret


def get_node_names(matrix):
    """Gets the node names from the matrix"""
    node_names = []
    (_, nodes) = matrix[0]
    for (node, _) in nodes.items():
        node_names.append(node.name)

    return node_names


def get_cells(matrix):
    """Generates the cells from the matrix"""
    cells = []
    cell = {}

    for row in matrix:
        (dist, nodes) = row

        for (node, weight) in dist.items():
            cell[node] = weight

        for (n1, n2) in nodes.items():
            cells.append('-' if n2 is None else f"{n2.name},{cell[n1]}")

    return cells


def matrix_str(matrix):
    """Returns the matrix object as a string"""

    ret = ""
    node_names = get_node_names(matrix)
    cells = get_cells(matrix)
    cell_width = max([len(x) for x in cells]) + 4

    header = "".center(cell_width)

    for s in node_names:
        header += s.center(cell_width)

    header += "\n" + ("-" * len(header)) + "\n"

    ret += header

    pos = 0

    for row in node_names:
        ret += row.ljust(cell_width - 1) + "|"

        for _ in range(len(node_names)):
            ret += cells[pos].center(cell_width)
            pos += 1
        ret += "\n"

    return ret


def main():
    graph = get_graph()

    matrix = []

    for node in graph:
        matrix.append((dijkstra(graph, node)))

    out = matrix_str(matrix)

    print(out)

    fout = open(get_outfile(), "w")
    print(get_outfile())
    fout.write(out)
    fout.close()


main()
