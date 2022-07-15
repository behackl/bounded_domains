from bounded_domains import Element, Node, PolygonalDomain, rectangle_domain_data

from pathlib import Path


def test_map_construction_tiny():
    domain = PolygonalDomain(
        [Element(0, [0, 1, 2]), Element(1, [1, 2, 3]), Element(2, [3, 4, 5])],
        [Node(0, 0), Node(1, 0), Node(0, 1), Node(1, 1), Node(2, 1), Node(1, 2)],
    )
    assert domain._node_containment_dict == {
        0: {0},
        1: {0, 1},
        2: {0, 1},
        3: {1, 2},
        4: {2},
        5: {2},
    }
    assert domain._adjacent_node_dict == {
        0: {1, 2},
        1: {0, 2, 3},
        2: {0, 1, 3},
        3: {1, 2, 4, 5},
        4: {3, 5},
        5: {3, 4},
    }
    assert domain.adjacent_elements(domain.elements[1], shared_edge=True) == {
        domain.elements[0]
    }


def test_generated_42x42_domain():
    elements, vertices = rectangle_domain_data(42, 42)
    domain = PolygonalDomain(elements, vertices)
    assert (
        repr(domain)
        == f"PolygonalDomain({len(elements)} elements, {len(vertices)} nodes)"
    )


def test_3x3_domain(request):
    domain = PolygonalDomain.from_files(
        Path(request.node.fspath).parent / "resources/3x3_elements_2d.txt",
        Path(request.node.fspath).parent / "resources/3x3_coords_2d.txt",
    )


def test_117x34_domain(request):
    domain = PolygonalDomain.from_files(
        Path(request.node.fspath).parent / "resources/117x34_elements_2d.txt",
        Path(request.node.fspath).parent / "resources/117x34_coords_2d.txt",
    )
