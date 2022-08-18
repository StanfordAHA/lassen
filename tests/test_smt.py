from hwtypes import BitVector, SMTBit, SMTBitVector
from hwtypes.modifiers import strip_modifiers

from peak.assembler.assembler import Assembler
from peak.assembler.assembled_adt import AssembledADT
from peak.family import PyFamily, SMTFamily
from peak.mapper.utils import aadt_product_to_dict


from lassen.mode import gen_register_mode
from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.lut import LUT_fc
from lassen.sim import PE_fc


def create_input(T):
    T = strip_modifiers(T)
    aadt_t = AssembledADT[T, Assembler, SMTBitVector]
    width = Assembler(T).width
    aadt_val = aadt_t(SMTBitVector[width]())
    return aadt_product_to_dict(aadt_val)


def test_LUT():
    LUT_smt = LUT_fc(SMTFamily())


def test_cond():
    Cond_smt = Cond_fc(SMTFamily())


def test_mode():
    rmode_smt = gen_register_mode(16, 0)(SMTFamily())


def test_alu():
    ALU_smt = ALU_fc(SMTFamily())


def test_PE():
    PE_smt = PE_fc(SMTFamily())
