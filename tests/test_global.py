import hwtypes
from lassen.sim import gen_pe
from lassen import Global


def test_irq_global():
    PE = gen_pe(hwtypes.BitVector.get_family())
    irq_type = PE.__call__._peak_outputs_["irq"]
    assert issubclass(irq_type, hwtypes.Bit)
    assert issubclass(irq_type, Global)
