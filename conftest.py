import pytest
from magma.backend.coreir_ import ResetCoreIR


@pytest.fixture(autouse=True)
def lassen_test():
    ResetCoreIR()
