import pytest

from bounded_domains import Element, Node, read_element_file, read_vertex_file


def test_read_element_file(tmp_path):
    filecontent = """2
0   1   2
1   2   3"""
    with open(tmp_path / "sample_elements.txt", "w") as file:
        file.write(filecontent)

    elements = read_element_file(tmp_path / "sample_elements.txt")
    assert elements == [Element(0, [0, 1, 2]), Element(1, [1, 2, 3])]


def test_read_element_file_mismatched_number(tmp_path):
    filecontent = """42
0   1   2
1   2   3"""
    with open(tmp_path / "sample_elements.txt", "w") as file:
        file.write(filecontent)

    with pytest.raises(ValueError):
        read_element_file(tmp_path / "sample_elements.txt")


def test_read_vertex_file(tmp_path):
    filecontent = """3
0       0
0.5     0.5
1.0     2.0"""
    with open(tmp_path / "sample_vertices.txt", "w") as file:
        file.write(filecontent)

    vertices = read_vertex_file(tmp_path / "sample_vertices.txt")
    assert vertices == [Node(0.0, 0.0), Node(0.5, 0.5), Node(1.0, 2.0)]


def test_read_vertex_file_mismatched_number(tmp_path):
    filecontent = """42
0       0
0.5     0.5
1.0     2.0"""
    with open(tmp_path / "sample_vertices.txt", "w") as file:
        file.write(filecontent)

    with pytest.raises(ValueError):
        read_vertex_file(tmp_path / "sample_vertices.txt")
