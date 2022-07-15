"""Data structures and classes for polygonal domains."""

from __future__ import annotations

import numpy as np

from collections import namedtuple, defaultdict
from pathlib import Path
from scipy.spatial import KDTree
from typing import Iterable

from . import logger


class Element:
    """Representation of a (triangular) element."""

    def __init__(self, id: int, vertices: Iterable[int]) -> None:
        self.id = id
        vertices = set(vertices)
        if len(vertices) != 3:
            raise ValueError(
                f"Element with index {id} is not a triangle; "
                f"passed vertex indices: {vertices}"
            )
        self.vertices = vertices

    def __repr__(self):
        return f"Element(id={self.id}, vertices={self.vertices})"


Node = namedtuple("Node", ["x", "y"])


class PolygonalDomain:
    """A polygonal domain consisting of (triangular) elements.

    Parameters
    ----------
    elements
        The list of elements the domain consists of.
    coordinates
        The list of Nodes specifying the coordinates of the
        elements of the domain.
    """

    def __init__(self, elements: list[Element], vertices: list[Node]) -> None:
        self.elements = elements

        self.build_mappings()
        self.build_node_tree(vertices)

    def __repr__(self):
        return (
            f"PolygonalDomain({len(self.elements)} elements, {self._node_tree.n} nodes)"
        )

    @staticmethod
    def from_files(
        element_file_path: str | Path, vertex_file_path: str | Path
    ) -> PolygonalDomain:
        """Constructs a PolygonalDomain by reading entries from files."""
        from .utils import read_element_file, read_vertex_file

        elements = read_element_file(element_file_path)
        vertices = read_vertex_file(vertex_file_path)
        return PolygonalDomain(elements, vertices)

    def build_mappings(self) -> None:
        """Iterate through domain elements and build auxiliary relation dictionaries."""
        self._node_containment_dict = defaultdict(set)
        self._adjacent_elements_shared_vertex_dict = defaultdict(set)
        self._adjacent_elements_shared_edge_dict = defaultdict(set)
        self._adjacent_node_dict = defaultdict(set)

        for element in self.elements:
            for vertex in element.vertices:
                self._node_containment_dict[vertex].add(element.id)

        logger.debug("Populated node containment dictionary.")

        # Given an element E, all adjacent elements can be
        # determined by considering the union of all elements
        # the vertices of E are contained in. The edge-adjacent
        # ones can then be filtered out.

        for element in self.elements:
            for vertex in element.vertices:
                adjacent_elements = self.elements_containing_vertex(vertex)
                self._adjacent_elements_shared_vertex_dict[element].update(
                    adjacent_elements
                )
                for adjacent_element in adjacent_elements:
                    self._adjacent_node_dict[vertex].update(adjacent_element.vertices)

            self._adjacent_elements_shared_vertex_dict[element].remove(element)

            edge_adjacent_elements = {
                adjacent_element
                for adjacent_element in self._adjacent_elements_shared_vertex_dict[
                    element
                ]
                if len(set.intersection(element.vertices, adjacent_element.vertices))
                == 2
            }
            self._adjacent_elements_shared_edge_dict[element] = edge_adjacent_elements

        logger.debug("Populated node and element adjacency dictionaries.")

    def build_node_tree(self, vertices: list[Node]) -> None:
        """Build auxiliary kd-tree used for distance queries."""
        coordinates = np.array([[v.x, v.y] for v in vertices])
        self._node_tree = KDTree(coordinates)
        logger.debug("Coordinate kd-tree has been constructed.")

    def vertex(self, node_index: int) -> Node:
        return Node(*self._node_tree.data[node_index])

    def elements_containing_vertex(self, vertex_index: int) -> list[Element]:
        return [self.elements[ind] for ind in self._node_containment_dict[vertex_index]]

    def adjacent_elements(
        self, element: Element, shared_edge: bool = False
    ) -> list[Element]:
        if shared_edge:
            return self._adjacent_elements_shared_edge_dict[element]
        return self._adjacent_elements_shared_vertex_dict[element]

    def adjacent_vertices(self, vertex_index: int) -> list[int]:
        return self._adjacent_node_dict[vertex_index]

    def distance_to_element(self, node: Node, element_id: int) -> float:
        r"""The distance from a given input Node to the element with the specified id.

        We use the following approach to determine the distance between
        the point :math:`P` and the triangle :math:`\triangle ABC`. First,
        we solve the equation :math:`A + (B-A) t_1 + (C-A) t_2 = P`. Depending
        on the values of :math:`t_1` and :math:`t_2`, we proceed as follows:

        - In case :math:`0\leq t_1, t_2 \leq 1` the point is inside of
          :math:`\triangle ABC` and the distance is thus 0,
        - if :math:`t_1 < 0` we compute the closest point on the segment :math:`AC`,
        - if :math:`t_2 < 0` we compute the closest point on the segment :math:`AB`,
        - and if :math:`t_1 + t_2 > 1` we compute the closest point on
          the segment :math:`BC`.

        Parameters
        ----------
        node
            The node to which the distance is computed.
        element_id
            The index of the element to which the distance is computed.
        """
        A, B, C = [
            np.array(self.vertex(ind)) for ind in self.elements[element_id].vertices
        ]
        P = np.array(node)

        t1, t2 = np.dot(np.linalg.inv(np.column_stack((B - A, C - A))), (P - A).T)
        logger.debug(f"Triangle {A, B, C} coordinates: t1={t1}, t2={t2}")

        if 0 <= t1 <= 1 and 0 <= t2 <= 1 and t1 + t2 <= 1:  # point inside of triangle
            return 0.0
        if t1 < 0:  # consider segment AC
            return distance_point_on_segment(P, A, C)
        if t2 < 0:  # consider segment AB
            return distance_point_on_segment(P, A, B)
        else:  # consider segment BC
            return distance_point_on_segment(P, B, C)

    def closest_vertex(self, node: Node) -> int:
        """Determines a closest vertex to the specified node.

        This is done by querying the kd-tree storing coordinate data.

        Parameters
        ----------
        node
            The node to which a closest vertex is determined.

        Returns
        -------
        int
            The index of a closest vertex.
        """
        distance, closest_vertex_index = self._node_tree.query(node)
        return closest_vertex_index

    def closest_element(
        self, node: Node, compare_all_elements: bool = False
    ) -> Element:
        """Determines a element of the domain that is closest to the specified node.

        The default, efficient strategy to find the closest element is as follows:

        - First, by calling :meth:`.closest_vertex`, the closest vertex
          of the polygonal domain is determined.
        - Second, :meth:`.elements_containing_vertex` is used to determine
          all elements which the closest vertex is contained in.
        - Third, the determined elements together with their adjacent ones
          (via :meth:`.adjacent_elements`) make up a set of candidate elements.
        - Finally, the distance to all elements in the candidate set is
          computed using :meth:`.distance_to_element`, and an Element with
          minimal distance is returned.

        .. NOTE::

            In pathologic situations where the polygonal domain is not
            connected, the strategy that only considers elements
            adjacent to the ones containing a closest vertex can produce
            wrong results.

        Parameters
        ----------
        node
            The node to which an element with minimum distance is found.
        compare_all_elements
            If False (the default) only elements adjacent to the ones
            containing the closest vertex are queried. Otherwise the
            distance to all elements is computed.
        """
        if compare_all_elements:
            candidate_set = self.elements
        else:
            closest_vertex = self.closest_vertex(node)
            candidate_set = self.elements_containing_vertex(closest_vertex)
            adjacent_elements = set()
            for element in candidate_set:
                adjacent_elements.update(self.adjacent_elements(element))
            candidate_set = set.union(adjacent_elements, candidate_set)

        return min(
            candidate_set, key=lambda elem: self.distance_to_element(node, elem.id)
        )


def distance_point_on_segment(P: Node, A: Node, B: Node):
    """Determines the shortest distance from a point P to a line segment AB."""
    p = np.array(P)
    a = np.array(A)
    b = np.array(B)
    segment_vector = b - a
    t = np.dot(p - a, segment_vector) / np.sum(segment_vector**2)
    if t < 0 or t > 1:  # projection outside of segment segment
        t = 0 if t < 0 else 1
    return np.linalg.norm(a + t * segment_vector - p)
