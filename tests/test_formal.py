"""
Formal equivalence checks between Peak SMTBitVector representation and magma
generated coreir
"""
import pytest
from hwtypes import SMTBitVector, SMTBit, BitVector
from lassen.sim import gen_pe
import lassen.smt_asm as smt_asm
import lassen.asm as bv_asm
import magma as m
import fault
import peak
from peak.auto_assembler import generate_assembler


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))


@pytest.mark.parametrize("op", ["add", "sub"])
def test_op(op):
    """
    Test add and sub op
    """
    smt_family = SMTBitVector.get_family()
    smt_PE = gen_pe(smt_family)

    smt_expression = smt_PE()(
        inst=getattr(smt_asm, op)(),
        data0=SMTBitVector[16](name="data0"),
        data1=SMTBitVector[16](name="data1"),
        bit0=SMTBit(name="bit0"),
        bit1=SMTBit(name="bit1"),
        bit2=SMTBit(name="bit2")
    )

    magma_PE = gen_pe(m.get_family())

    bv_pe = gen_pe(BitVector.get_family())
    instr_name, inst_type = bv_pe().__call__._peak_isa_
    assembler, disassembler, width, layout = \
                generate_assembler(inst_type)
    instr_magma_type = type(magma_PE.interface.ports[instr_name])
    pe_circuit = peak.wrap_with_disassembler(magma_PE, disassembler, width,
                                             HashableDict(layout),
                                             instr_magma_type)

    tester = fault.SymbolicTester(pe_circuit, pe_circuit.CLK)
    inst = assembler(getattr(bv_asm, op)())
    print(type(inst))
    tester.circuit.inst.assume(inst)
    print(type(smt_expression[0]))
    tester.circuit.O0.guarantee(smt_expression[0])
    # tester.circuit.O1.guarantee(smt_expression[1])
    # tester.circuit.O2.guarantee(smt_expression[2])

    # tester.compile_and_run("cosa", directory="tests/build",
    #                        magma_opts={"passes": ["rungenerators", "flatten",
    #                                               "cullgraph"]})
    m.compile("tests/build/WrappedPE", pe_circuit, output="coreir-verilog")
    import os
    os.system("cat tests/build/CW_fp_add.v tests/build/CW_fp_mult.v"
              " tests/build/WrappedPE.v > tests/build/WrappedPE_tmp.v")
    os.system("mv tests/build/WrappedPE_tmp.v tests/build/WrappedPE.v")
    tester.compile_and_run("cosa", skip_compile=True, directory="tests/build",
                           solver="z3")
