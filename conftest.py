import pytest
from magma.frontend.coreir_ import ResetCoreIR


@pytest.fixture(autouse=True)
def lassen_test():
    ResetCoreIR()
