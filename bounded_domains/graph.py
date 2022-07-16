"""Graph structure and auxiliary constructs for representation of polygonal domains."""

from __future__ import annotations

from .structures import PolygonalDomain

import gzip
import json
import matplotlib
import numpy as np

from matplotlib import pyplot as plt
from pathlib import Path
from typing import Iterator

class SparseMatrix:
    """A sparse matrix implementing the CRS format.

    Parameters
    ----------
    array
        A two-dimensional (rectangular) array of floats. Only non-zero
        entries will be stored.
    """

    def __init__(self, array: list[list[float]]) -> None:
        self.values = []
        self.column_indices = []
        self.row_pointers = [0]
        self._columns = len(array[0])

        number_of_entries = 0
        for row in array:
            for index, element in enumerate(row):
                if element != 0:
                    self.values.append(element)
                    self.column_indices.append(index)
                    number_of_entries += 1
            self.row_pointers.append(number_of_entries)

    @property
    def columns(self):
        """The number of columns in the matrix."""
        return self._columns

    @property
    def rows(self):
        """The number of rows in the matrix."""
        return len(self.row_pointers) - 1

    def __repr__(self) -> None:
        return f"SparseMatrix({self.rows}x{self.columns}, {len(self.values)} entries)"

    def __eq__(self, other: SparseMatrix) -> bool:
        return (
            self.values == other.values and
            self.column_indices == other.column_indices and
            self.row_pointers == other.row_pointers and
            self.columns == other.columns
        )

    def __getitem__(self, key: tuple[int, int]) -> float:
        """Array-indexing, allows to query entries via SparseMatrix[i, j]"""
        i, j = key
        nonempty_columns = self.column_indices[
            self.row_pointers[i] : self.row_pointers[i + 1]
        ]
        try:
            column_index = nonempty_columns.index(j)
            return self.values[self.row_pointers[i] + column_index]
        except ValueError:
            return 0

    def __matmul__(self, other: np.ndarray) -> np.ndarray:
        """Matrix-vector multiplication using the @ operator.

        .. WARNING::

            This *only* implements matrix-vector multiplication, it cannot be used
            to multiply two instances of :class:`.SparseMatrix` with each other.
        """
        result = []
        values_iter = iter(self.values)
        for i in range(self.rows):
            result_entry = 0
            for j in range(self.row_pointers[i], self.row_pointers[i + 1]):
                result_entry += next(values_iter) * other[self.column_indices[j]]
            result.append(result_entry)

        return np.array(result)

    def cell_iterator(self) -> Iterator[tuple[tuple[int, int], float]]:
        """An iterator over all non-zero entries with their matrix coordinates."""
        row = 0
        for index, value in enumerate(self.values):
            column = self.column_indices[index]
            while self.row_pointers[row+1] <= index:
                row += 1
            yield ((row, column), value)

    @staticmethod
    def from_CRS(
        values: list[float],
        column_indices: list[int],
        row_pointers: list[int],
        columns: int
    ) -> SparseMatrix:
        """Initialization of a SparseMatrix from the raw CRS data.

        Parameters
        ----------
        values
            The list of non-zero entries.
        column_indices
            The list of column indices of the non-zero entries.
        row_pointers
            The list containing the (cumulative) number of non-zero
            entries.
        columns
            The number of columns of the matrix.
        """
        mat = SparseMatrix([[]])
        mat.values = values
        mat.column_indices = column_indices
        mat.row_pointers = row_pointers
        mat._columns = columns
        return mat

    def save(self, filename: str | Path, binary: bool = False) -> None:
        """Save the matrix to a file.

        Parameters
        ----------
        filename
            The name of the file the matrix will be stored in.
        binary
            If False (the default), the matrix will be written to a
            plain text ASCII file (rows are newline-separated, entries
            are tab-separated). Otherwise the matrix is written to a
            compressed (via gzip) binary file.
        """
        if not binary:
            matrix_string = "\n".join(
                "\t".join(
                    str(self[i, j]) for j in range(self.columns)
                ) for i in range(self.rows)
            )
            with open(filename, 'w') as file:
                file.write(matrix_string)

        else:
            data = {
                'values': self.values,
                'column_indices': self.column_indices,
                'row_pointers': self.row_pointers,
                'columns': self.columns,
            }
            serialized_data = json.dumps(data).encode('utf-8')
            with gzip.open(filename, 'w') as file:
                file.write(serialized_data)


    @staticmethod
    def read(filename: str | Path) -> None:
        """Read a sparse matrix from a file.

        The file can either be an ASCII file (with rows separated by newlines,
        and space-separated entries), or a binary file created with
        :meth:`.SparseMatrix.save`.

        Parameters
        ----------
        filename
            The name of the file to be read.
        """
        bad_gzip_exception = getattr(gzip, 'BadGzipFile', OSError)
        try:
            with gzip.open(filename, 'r') as file:
                serialized_data = file.read().decode('utf-8')
                data = json.loads(serialized_data)
                return SparseMatrix.from_CRS(**data)
        except bad_gzip_exception:
            with open(filename, 'r') as file:
                array = []
                for line in file:
                    array.append([float(val) for val in line.split()])

            return SparseMatrix(array)


    def plot(self, filename: str | Path | None = None) -> None:
        """A plot of this matrix.

        Parameters
        ----------
        filename
            The name of the file the plot is written to. If None (the default),
            matplotlib just shows the plot.
        """
        _ = plt.figure()
        plt.matshow(
            [[self[i, j] for j in range(self.columns)] for i in range(self.rows)]
        )
        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)



class Graph:
    """A graph modeling the relationship of vertices in a polygonal domain.

    The graph is stored in form of an adjacency matrix (using :class:`.SparseMatrix`).

    Parameters
    ----------
    domain
        The :class:`.PolygonalDomain` whose vertices should be modeled by the graph.
    """

    def __init__(self, domain: PolygonalDomain) -> None:
        adjacency_array = []
        for vertex in range(domain.num_vertices):
            adjacent_vertices = domain.adjacent_vertices(vertex)
            adjacency_array.append([
                1 if w in adjacent_vertices else 0
                for w in range(domain.num_vertices)
            ])

        self._adjacency_matrix = SparseMatrix(adjacency_array)
        self._node_positions = domain._node_tree.data

    def __repr__(self) -> str:
        return f"Graph({self.order} vertices, {self.size} edges)"

    @property
    def order(self) -> int:
        """The order of the graph, i.e., the number of vertices."""
        return self._adjacency_matrix.rows

    @property
    def size(self) -> int:
        """The size of the graph, i.e., the number of edges."""
        return len(self._adjacency_matrix.values)

    def plot(self, filename: str | Path | None = None, **kwargs) -> None:
        """A plot of the graph.

        .. NOTE::

            For the sake of visual clarity, the reflexive
            edges are not plotted. For the other edges, their
            color corresponds to their weight.

        Parameters
        ----------
        filename
            The name of the file the plot is saved to.
        kwargs
            Further keyword arguments are passed to matplotlib.
        """
        _ = plt.figure(**kwargs)
        min_value = min(self._adjacency_matrix.values)
        max_value = max(self._adjacency_matrix.values)
        colormap = matplotlib.cm.get_cmap("coolwarm")
        for ((i, j), value) in self._adjacency_matrix.cell_iterator():
            plt.plot(
                (self._node_positions[i, 0], self._node_positions[j, 0]),
                (self._node_positions[i, 1], self._node_positions[j, 1]),
                c=colormap((value - min_value)/(max_value - min_value)),
            )
        plt.plot(
            self._node_positions[:,0],
            self._node_positions[:,1],
            'o',
            c='#000'
        )
        if filename is not None:
            plt.savefig(filename)
        else:
            plt.show()


class WeightedGraph(Graph):
    """A weighted graph modeling the relationship of vertices in a polygonal domain.

    The weight of an edge between distinct vertices :math:`u` and :math:`v`
    is the inverse of the squared node distance. The weight of reflexive
    edges :math:`(v, v)` is the negative sum of the weights of all non-reflexive
    edges incident to :math:`v`.

    Parameters
    ----------
    domain
        The :class:`.PolygonalDomain` whose vertices should be modeled by the graph.
    """
    def __init__(self, domain: PolygonalDomain) -> None:
        super().__init__(domain)
        for index, tp in enumerate(self._adjacency_matrix.cell_iterator()):
            ((i, j), value) = tp
            if i != j:
                vec_i = np.array(domain.vertex(i))
                vec_j = np.array(domain.vertex(j))
                self._adjacency_matrix.values[index] = 1 / np.sum((vec_i - vec_j)**2)
            else:
                weight_sum = 0
                vec_i = np.array(domain.vertex(i))
                for k in domain.adjacent_vertices(i):
                    if k == i:
                        continue
                    vec_k = np.array(domain.vertex(k))
                    weight_sum += 1 / np.sum((vec_i - vec_k)**2)
                self._adjacency_matrix.values[index] = -weight_sum

    def __repr__(self) -> str:
        return f"WeightedGraph({self.order} vertices, {self.size} edges)"
