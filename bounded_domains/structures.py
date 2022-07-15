"""Data structures and classes for polygonal domains."""

from __future__ import annotations

from typing import Iterable

from collections import namedtuple, defaultdict
from pathlib import Path


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


Node = namedtuple('Node', ['x', 'y'])



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
    # needs to be initialized with element list and coordinate list
    # probably implements the actual computations
    def __init__(self, elements: list[Element], coordinates: list[Node]) -> None:
        self.elements = elements
        self.coordinates = coordinates

        self.build_mappings()
        self.build_quadtree()


    def __repr__(self):
        return f"PolygonalDomain({len(self.elements)} elements, {len(self.coordinates)} nodes)"

    @staticmethod
    def from_files(element_file_path: str | Path, vertex_file_path: str | Path) -> PolygonalDomain:
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
                self._adjacent_elements_shared_vertex_dict[element].update(adjacent_elements)
                for adjacent_element_id in adjacent_elements:
                    adjacent_element = self.elements[adjacent_element_id]
                    self._adjacent_node_dict[vertex].update(adjacent_element.vertices)

            self._adjacent_elements_shared_vertex_dict[element].remove(element.id)

            edge_adjacent_elements = {
                self.elements[id] for id
                in self._adjacent_elements_shared_vertex_dict[element]
                if len(set.intersection(element.vertices,
                                        self.elements[id].vertices)) == 2
            }
            self._adjacent_elements_shared_edge_dict[element] = edge_adjacent_elements

        for vertex, neighbors in self._adjacent_node_dict.items():
            neighbors.remove(vertex)


    def build_quadtree(self) -> None:
        """Iterate through domain vertices and build auxiliary quadtree."""
        self._quadtree = None

        # TODO: build quadtree

    def elements_containing_vertex(self, vertex_index: int) -> list[Element]:
        return self._node_containment_dict[vertex_index]

    def adjacent_elements(
        self,
        element: Element,
        shared_edge: bool = False
        ) -> list[Element]:
        if shared_edge:
            return self._adjacent_elements_shared_edge_dict[element]
        return self._adjacent_elements_shared_vertex_dict[element]

    def adjacent_vertices(self, vertex_index: int) -> list[int]:
        return self._adjacent_node_dict[vertex_index]

    def closest_element(self, node: Node, return_index: bool = False) -> Element | int:
        """Determines a element of the domain that is closest to the specified node.

        Parameters
        ----------
        node
            The node to which an element with minimum distance is found.
        return_index
            If False (the default), the actual element is returned. Otherwise
            the element index in the domain is returned.
        """
        return 0

