import pytest
from hwtypes import SIntVector, UIntVector, BitVector, Bit
from peak.family import PyFamily
import lassen.asm as asm
from lassen import PE_fc, Inst_fc
from lassen.common import DATAWIDTH, BFloat16_fc
from rtl_utils import rtl_tester, CAD_ENV


Inst = Inst_fc(PyFamily())
Mode_t = Inst.rega

PE = PE_fc(PyFamily())
pe = PE()

BFloat16 = BFloat16_fc(PyFamily())
Data = BitVector[DATAWIDTH]


def test_fp_mul_rounding():
    inst = asm.fp_mul()
    data0 = Data(0x42c8)
    data1 = Data(0x3fb9)

    res, res_p, _, _, _ = pe(inst, data0, data1)
    if CAD_ENV:
        rtl_tester(inst, data0, data1, res=res)
    else:
        pytest.skip("Skipping since CW not available")
