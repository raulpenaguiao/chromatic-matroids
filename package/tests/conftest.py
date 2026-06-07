import pytest
from chromatic_matroids import (
    Composition, SetComposition, Matroid, QSymFunction, NCQSymFunction,
    uniform_matroid, schubert_matroid, nested_matroid, graphic_matroid,
)


@pytest.fixture
def u21():
    return uniform_matroid(2, 1)


@pytest.fixture
def u32():
    return uniform_matroid(3, 2)


@pytest.fixture
def k3():
    return graphic_matroid([(1, 2), (1, 3), (2, 3)], {1, 2, 3})
