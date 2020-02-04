from lassen.mode import gen_register_mode
from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.lut import LUT_fc
from lassen.sim import PE_fc
from hwtypes import BitVector, SMTBit
import magma


def test_LUT():
    LUT_SMTBit = LUT_fc(SMTBit.get_family())

def test_cond():
    Cond_SMTBit = Cond_fc(SMTBit.get_family())

def test_mode():
    rmode_SMTBit = gen_register_mode(BitVector[16], 0)(SMTBit.get_family())

def test_alu():
    ALU_SMTBit = ALU_fc(SMTBit.get_family())

def test_PE():
    PE_SMTBit = PE_fc(SMTBit.get_family())

