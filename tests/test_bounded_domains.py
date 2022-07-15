from bounded_domains import __version__, Element, Node, PolygonalDomain


def test_version():
    assert __version__ == '0.1.0'


def test_map_construction_tiny():
    domain = PolygonalDomain(
        [Element(0, [0, 1, 2]), Element(1, [1, 2, 3]), Element(2, [3, 4, 5])],
        [Node(0, 0), Node(1, 0), Node(0, 1), Node(1, 1), Node(2, 1), Node(1, 2)]
    )
    assert domain._node_containment_dict == {0: {0}, 1: {0, 1}, 2: {0, 1}, 3: {1, 2}, 4: {2}, 5: {2}}
    assert domain._adjacent_node_dict == {0: {1, 2}, 1: {0, 2, 3}, 2: {0, 1, 3}, 3: {1, 2, 4, 5}, 4: {3, 5}, 5: {3, 4}}
    assert domain.adjacent_elements(domain.elements[1], shared_edge=True) == {domain.elements[0]}
