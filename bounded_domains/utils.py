"""Utility functions (in particular file operations)."""

from __future__ import annotations

from pathlib import Path

from . import logger
from .domains import Element, Node


def read_element_file(file_path: Path | str) -> list[Element]:
    """Read an element file and return its content in a list.

    Also checks whether the specified file is formatted correctly.

    An element file is a plain text file formatted like this::

        number of Elements
        vertex1     vertex2     vertex3
        vertex1     vertex2     vertex3
        ...

    The vertices are given in form of integer indices referring to
    the corresponding entry in the vertex file.

    Parameters
    ----------
    file_path
        The path to the element file.
    """
    with open(file_path, "r") as element_file:
        num_elements = int(next(element_file).strip())  # first line of file
        elements = []
        for element_index, line in enumerate(element_file):
            vertex_indices = [int(v_index) for v_index in line.split()]
            elements.append(Element(element_index, vertex_indices))

        if num_elements != len(elements):
            raise ValueError(
                f"Specified number of elements {num_elements} does not match "
                f"number of read elements {len(elements)}"
            )
        logger.info(f"Read {num_elements} elements from {file_path}")
        return elements


def read_vertex_file(file_path: Path | str) -> list[Node]:
    """Read a vertex file and return its content in a list.

    Also checks whether the specified file is formatted correctly.

    A vertex file is a plain text file formatted like this::

        number of coordinates
        x   y
        x   y
        ...

    The x and y coordinates are given as floats.

    Parameters
    ----------
    file_path
        The path to the vertex file.
    """
    with open(file_path, "r") as vertex_file:
        num_vertices = int(next(vertex_file).strip())
        vertices = []
        for line in vertex_file:
            vertices.append(Node(*[float(coord) for coord in line.split()]))

        if num_vertices != len(vertices):
            raise ValueError(
                f"Specified number of vertices {num_vertices} does not match "
                f"number of read vertices {len(vertices)}"
            )
        logger.info(f"Read {num_vertices} from {file_path}")
        return vertices


def rectangle_domain_data(m: int, n: int) -> tuple(list[Element], list[Node]):
    """Generate data for a triangulation of the unit square.

    Parameters
    ----------
    n
        The number of intervals along the x-axis.
    m
        The number of intervals along the y-axis.

    Returns
    -------
        A tuple with the first entry being the list of elements
        and the second entry being the list of nodes required
        to instantiate a :class:`.PolygonalDomain`.
    """
    vertices = [Node(x=i / n, y=j / m) for i in range(n + 1) for j in range(m + 1)]
    # vertex at (i/n, j/m) has index i*(m+1) + j.
    lower_triangles = [
        [i * (m + 1) + j, i * (m + 1) + j + 1, (i + 1) * (m + 1) + j]
        for i in range(n)
        for j in range(m)
    ]
    upper_triangles = [
        [(i + 1) * (m + 1) + j, (i + 1) * (m + 1) + j + 1, i * (m + 1) + j + 1]
        for i in range(n)
        for j in range(m)
    ]
    elements = [
        Element(id, triangle)
        for id, triangle in enumerate(lower_triangles + upper_triangles)
    ]
    return elements, vertices
