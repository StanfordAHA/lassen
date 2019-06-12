"""
Test RegisterMode RTL
"""

import magma as m
from lassen.family import gen_pe_type_family
import hwtypes
import fault
from lassen.mode import gen_register_mode, gen_mode_type


def test_register_mode_const():
    Reg = gen_register_mode(m.Bits[16])
    Mode = gen_mode_type(gen_pe_type_family(hwtypes.BitVector.get_family()))

    tester = fault.Tester(Reg, Reg.CLK)

    tester.circuit.mode = Mode.CONST
    tester.circuit.value = 2
    tester.circuit.clk_en = 0
    tester.circuit.config_we = 0
    tester.circuit.config_data = 4
    tester.circuit.const_ = 0xDEAD
    tester.eval()
    tester.circuit.O0.expect(0xDEAD)
    tester.circuit.const_ = 0xBEEF
    tester.eval()
    tester.circuit.O0.expect(0xBEEF)
    tester.compile_and_run("verilator", flags=["-Wno-UNUSED"],
                           directory="tests/build")


def test_register_mode_bypass():
    Reg = gen_register_mode(m.Bits[16])
    Mode = gen_mode_type(gen_pe_type_family(hwtypes.BitVector.get_family()))

    tester = fault.Tester(Reg, Reg.CLK)

    tester.circuit.mode = Mode.BYPASS
    tester.circuit.value = 2
    tester.circuit.clk_en = 0
    tester.circuit.config_we = 0
    tester.circuit.config_data = 4
    tester.circuit.const_ = 0xDEAD
    tester.eval()
    tester.circuit.O0.expect(2)
    tester.circuit.value = 0xDEAD
    tester.eval()
    tester.circuit.O0.expect(0xDEAD)
    tester.circuit.value = 0xBEEF
    tester.eval()
    tester.circuit.O0.expect(0xBEEF)
    tester.compile_and_run("verilator", flags=["-Wno-UNUSED"],
                           directory="tests/build")


def test_register_mode_delay():
    Reg = gen_register_mode(m.Bits[16])
    Mode = gen_mode_type(gen_pe_type_family(hwtypes.BitVector.get_family()))

    tester = fault.Tester(Reg, Reg.CLK)

    tester.circuit.mode = Mode.DELAY
    tester.circuit.value = 2
    tester.circuit.clk_en = 0
    tester.circuit.config_we = 0
    tester.circuit.config_data = 4
    tester.circuit.const_ = 0xDEAD
    tester.step(2)
    tester.circuit.O0.expect(0)
    tester.circuit.value = 0xDEAD
    tester.step(2)
    tester.circuit.O0.expect(2)
    tester.circuit.value = 0xBEEF
    tester.step(2)
    tester.circuit.O0.expect(0xDEAD)
    tester.step(2)
    tester.circuit.O0.expect(0xBEEF)
    tester.compile_and_run("verilator", flags=["-Wno-UNUSED"],
                           directory="tests/build")
