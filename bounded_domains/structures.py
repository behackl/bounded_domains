"""Data structures and classes for polygonal domains."""

from __future__ import annotations

from collections import namedtuple
from pathlib import Path


from . import logger



class Element:
    """Representation of a (triangular) element."""
    def __init__(self, *vertex_ids) -> None:
        self.vertices = set(vertex_ids)


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
        self._node_containment_dict = None
        self._adjacent_element_dict = None
        self._adjacent_node_dict = None

        # TODO: iterate through element list once, build dictionaries.

    def build_quadtree(self) -> None:
        """Iterate through domain vertices and build auxiliary quadtree."""
        self._quadtree = None

        # TODO: build quadtree

    def elements_containing_vertex(self, vertex_index: int) -> list[Element]:
        return self._node_containment_dict[vertex_index]

    def adjacent_elements(self, element: Element) -> list[Element]:
        return self._adjacent_element_dict[element]

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

