from bounded_domains import SparseMatrix, Graph, WeightedGraph

import matplotlib
import numpy as np

from pathlib import Path


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