import pytest
import magma.backend.coreir_


@pytest.fixture(autouse=True)
def lassen_test():
    magma.backend.coreir_.__reset_context()

