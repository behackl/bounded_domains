from pathlib import Path

import matplotlib
import numpy as np

from bounded_domains import (
    Graph,
    SparseMatrix,
    WeightedGraph,
    PolygonalDomain,
    rectangle_domain_data,
)


def test_matrix_creation():
    mat = SparseMatrix(
        [
            [10, 0, 0, 12, 0],
            [0, 0, 11, 0, 13],
            [0, 16, 0, 0, 0],
            [0, 0, 11, 0, 13],
        ]
    )
    assert repr(mat) == "SparseMatrix(4x5, 7 entries)"
    assert mat.values == [10, 12, 11, 13, 16, 11, 13]
    assert mat.column_indices == [0, 3, 2, 4, 1, 2, 4]
    assert mat.row_pointers == [0, 2, 4, 5, 7]


def test_identity_matrix_multiplication():
    mat = SparseMatrix(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    )
    np.testing.assert_allclose(mat @ np.array([1, 42, -5]), np.array([1, 42, -5]))

    for _ in range(20):
        vector = np.random.rand(3)
        np.testing.assert_allclose(mat @ vector, vector)


def test_matrix_multiplication():
    mat = SparseMatrix(
        [
            [10, 0, 0, 12, 0],
            [0, 0, 11, 0, 13],
            [0, 16, 0, 0, 0],
            [0, 0, 11, 0, 13],
        ]
    )
    np.testing.assert_allclose(
        mat @ np.array([1, 1, 1, 1, 1]), np.array([22, 24, 16, 24])
    )


def test_matrix_getitem():
    mat = SparseMatrix(
        [
            [10, 0, 0, 12, 0],
            [0, 0, 11, 0, 13],
            [0, 16, 0, 0, 0],
            [0, 0, 11, 0, 13],
        ]
    )
    assert mat[0, 0] == 10
    assert mat[0, 3] == 12
    assert mat[1, 1] == 0


def test_matrix_cell_iterator():
    mat = SparseMatrix(
        [
            [10, 0, 0, 12, 0],
            [0, 0, 11, 0, 13],
            [0, 16, 0, 0, 0],
            [0, 0, 11, 0, 13],
        ]
    )
    assert list(mat.cell_iterator()) == [
        ((0, 0), 10),
        ((0, 3), 12),
        ((1, 2), 11),
        ((1, 4), 13),
        ((2, 1), 16),
        ((3, 2), 11),
        ((3, 4), 13),
    ]


def test_matrix_from_CRS():
    mat = SparseMatrix.from_CRS(
        values=[10, 12, 11, 13, 16, 11, 13],
        column_indices=[0, 3, 2, 4, 1, 2, 4],
        row_pointers=[0, 2, 4, 5, 7],
        columns=5,
    )
    assert mat == SparseMatrix(
        [
            [10, 0, 0, 12, 0],
            [0, 0, 11, 0, 13],
            [0, 16, 0, 0, 0],
            [0, 0, 11, 0, 13],
        ]
    )


def test_matrix_write_read(tmp_path):
    mat = SparseMatrix(
        [
            [10, 0, 0, 12, 0],
            [0, 0, 11, 0, 13],
            [0, 16, 0, 0, 0],
            [0, 0, 11, 0, 13],
        ]
    )
    mat.save(tmp_path / "matrix.gz", binary=True)
    mat.save(tmp_path / "matrix.txt")
    read_bin_mat = SparseMatrix.read(tmp_path / "matrix.gz")
    assert mat == read_bin_mat
    read_txt_mat = SparseMatrix.read(tmp_path / "matrix.txt")
    assert mat == read_txt_mat


def test_matrix_plot(tmp_path):
    np.random.seed(42)
    matplotlib.use("agg")
    mat = SparseMatrix(np.clip(np.random.rand(10, 10) - 0.5, 0, 1))
    mat.plot(tmp_path / "matrixplot.png")
    assert Path(tmp_path / "matrixplot.png").exists()


def test_graph_2x2():
    domain = PolygonalDomain(*rectangle_domain_data(2, 2))
    graph_2x2 = Graph(domain)

    assert graph_2x2.order == 9
    assert graph_2x2.size == 2 * 16 + 9
    assert repr(graph_2x2) == "Graph(9 vertices, 41 edges)"

    weighted_graph_2x2 = WeightedGraph(domain)
    assert repr(weighted_graph_2x2) == "WeightedGraph(9 vertices, 41 edges)"
    assert set(weighted_graph_2x2._adjacency_matrix.values) == set(
        [2.0, 4.0, -8.0, -10.0, -14.0, -20.0]
    )


def test_graph_plot(tmp_path):
    domain = PolygonalDomain(*rectangle_domain_data(5, 5))
    matplotlib.use("agg")
    graph = WeightedGraph(domain)
    graph.plot(tmp_path / "graphplot.png")
    assert Path(tmp_path / "graphplot.png").exists()


def test_weighted_graph_117_34():
    domain = PolygonalDomain(*rectangle_domain_data(117, 34))
    graph_117x34 = WeightedGraph(domain)

    assert graph_117x34.order == (117 + 1) * (34 + 1)
