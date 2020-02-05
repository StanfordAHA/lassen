from lassen.mode import gen_register_mode
from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.lut import LUT_fc
from lassen.sim import PE_fc
from hwtypes import BitVector, SMTBit, SMTBitVector
from peak.assembler.assembler import Assembler
from peak.assembler.assembled_adt import AssembledADT
from peak.mapper.utils import aadt_product_to_dict

def create_input(T):
    aadt_t = AssembledADT[T, Assembler, SMTBitVector]
    width = Assembler(T).width
    aadt_val = aadt_t(SMTBitVector[width]())
    return aadt_product_to_dict(aadt_val)

def test_LUT():
    LUT_smt = LUT_fc(SMTBit.get_family())
    inputs = create_input(LUT_smt.input_t)
    outputs = LUT_smt()(**inputs)

def test_cond():
    Cond_smt = Cond_fc(SMTBit.get_family())
    inputs = create_input(Cond_smt.input_t)
    outputs = Cond_smt()(**inputs)

def test_mode():
    rmode_smt = gen_register_mode(BitVector[16], 0)(SMTBit.get_family())
    inputs = create_input(rmode_smt.input_t)
    outputs = rmode_smt()(**inputs)

def test_alu():
    ALU_smt = ALU_fc(SMTBit.get_family())
    inputs = create_input(ALU_smt.input_t)
    outputs = ALU_smt()(**inputs)

def test_PE():
    PE_smt = PE_fc(SMTBit.get_family())
    inputs = create_input(PE_smt.input_t)
    outputs = PE_smt()(**inputs)

