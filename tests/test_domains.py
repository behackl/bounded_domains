from pathlib import Path

import numpy as np
import pytest

from bounded_domains import (
    Element,
    Node,
    PolygonalDomain,
    distance_point_on_segment,
    rectangle_domain_data,
)


def test_element():
    elem = Element(42, [1, 100, 10000])
    assert repr(elem) == "Element(id=42, vertices=[1, 100, 10000])"


def test_element_no_triangle():
    with pytest.raises(ValueError):
        Element(42, [1, 2, 3, 4])


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
        0: {0, 1, 2},
        1: {0, 1, 2, 3},
        2: {0, 1, 2, 3},
        3: {1, 2, 3, 4, 5},
        4: {3, 4, 5},
        5: {3, 4, 5},
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


def test_distance_point_to_segment():
    assert distance_point_on_segment(Node(5, 0), Node(0, 1), Node(1, 0)) == 4.0
    assert distance_point_on_segment(
        Node(0, 0), Node(0, 1), Node(1, 0)
    ) == np.linalg.norm([0.5, 0.5])
    assert distance_point_on_segment(Node(1, 0), Node(0, 1), Node(1, 0)) == 0.0


def test_distance_to_element():
    elements, vertices = rectangle_domain_data(1, 1)
    domain = PolygonalDomain(elements, vertices)
    assert domain.distance_to_element(Node(0, -1), 0) == 1.0
    assert domain.distance_to_element(Node(-0.42, 0), 0) == 0.42
    assert domain.distance_to_element(Node(0.25, 0.25), 0) == 0.0
    assert domain.distance_to_element(Node(1, -10), 1) == 10.0


def test_distance_to_element2():
    domain = PolygonalDomain(
        [Element(0, [0, 1, 2])], [Node(0, 0), Node(2, 1), Node(4, 0)]
    )
    assert domain.distance_to_element(Node(6, 4), 0) == np.sqrt(20)


def test_closest_element_randomized():
    elements, vertices = rectangle_domain_data(1, 1)
    domain = PolygonalDomain(elements, vertices)
    for _ in range(100):
        p = np.random.rand(2) * 2 - 0.5
        if p[0] - p[1] >= 1 or p[0] - p[1] <= -1:
            continue  # closest point is in a corner where 2 elements meet
        if sum(p) > 1:
            assert domain.closest_element(p).id == 1
        if sum(p) < 1:
            assert domain.closest_element(p).id == 0


def test_closest_element_compare_all_elements():
    domain = PolygonalDomain(*rectangle_domain_data(2, 2))
    assert domain.closest_element([1.1, 0.9], compare_all_elements=True).id == 7


def test_3x3_domain(request):
    domain = PolygonalDomain.from_files(
        Path(request.node.fspath).parent / "resources/3x3_elements_2d.txt",
        Path(request.node.fspath).parent / "resources/3x3_coords_2d.txt",
    )
    assert repr(domain) == "PolygonalDomain(18 elements, 16 nodes)"

    assert set(elem.id for elem in domain.adjacent_elements(3)) == {
        0,
        1,
        2,
        5,
        6,
        8,
        9,
        10,
        11,
    }
    assert set(elem.id for elem in domain.adjacent_elements(3, shared_edge=True)) == {
        0,
        2,
        8,
    }


def test_117x34_domain(request):
    domain = PolygonalDomain.from_files(
        Path(request.node.fspath).parent / "resources/117x34_elements_2d.txt",
        Path(request.node.fspath).parent / "resources/117x34_coords_2d.txt",
    )
    assert repr(domain) == "PolygonalDomain(7956 elements, 4130 nodes)"
