from collections import OrderedDict

from hwtypes import BitVector
import magma
import peak
from peak.family import PyFamily, MagmaFamily
from peak.assembler import Assembler

from lassen.alu import ALU_fc
from lassen.cond import Cond_fc
from lassen.lut import LUT_fc
from lassen.mode import gen_register_mode
from lassen.sim import PE_fc

magma_family = MagmaFamily()


def test_cond():
    Cond_magma = Cond_fc(magma_family)


def test_mode():
    rmode_magma = gen_register_mode(16, 0)(magma_family)


def test_alu():
    ALU_magma = ALU_fc(magma_family)


def test_PE():
    PE_magma = PE_fc(magma_family)


def test_LUT():
    LUT_magma = LUT_fc(magma_family)


def test_wrapped_PE():
    class HashableDict(dict):
        def __hash__(self):
            return hash(tuple(sorted(self.keys())))

    pe = PE_fc(PyFamily())
    # Lassen's name for the ISA is 'inst', so this is hardcoded
    __instr_name = "inst"
    __instr_type = pe.input_t.field_dict["inst"]
    __inputs = OrderedDict(pe.input_t.field_dict)
    __inputs["inst"]
    __outputs = OrderedDict(pe.output_t.field_dict)
    circuit = PE_fc(magma_family)
    __asm = Assembler(__instr_type)
    instr_magma_type = type(circuit.interface.ports[__instr_name])
    __circuit = peak.wrap_with_disassembler(
        circuit,
        __asm.disassemble,
        __asm.width,
        HashableDict(__asm.layout),
        instr_magma_type,
    )
    assert __circuit is not None
