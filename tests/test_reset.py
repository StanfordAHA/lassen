from lassen.mode import gen_mode_type
from lassen.family import gen_pe_type_family
from lassen.isa import gen_inst_type
from lassen.sim import gen_pe
from lassen.asm import add
import magma as m
import fault
import hwtypes
import peak
from peak.auto_assembler import generate_assembler
from test_pe import HashableDict


def test_reset():
    sim_family = gen_pe_type_family(hwtypes.BitVector.get_family())
    inst_type = gen_inst_type(sim_family)
    Mode = gen_mode_type(sim_family)
    assembler, disassembler, width, layout = generate_assembler(inst_type)
    PE = gen_pe(m.get_family(), use_assembler=True)
    PE = peak.wrap_with_disassembler(PE, disassembler, width,
                                     HashableDict(layout),
                                     type(PE.interface.ports["inst"]))
    tester = fault.Tester(PE, PE.CLK)

    inst = add(ra_mode=Mode.DELAY, rb_mode=Mode.DELAY)
    tester.circuit.inst = assembler(inst)
    data = [0, 0]
    for i in range(2):
        while data[i] == 0:
            data[i] = hwtypes.BitVector.random(16)
    tester.circuit.data0 = data[0]
    tester.circuit.data1 = data[1]
    tester.circuit.CLK = 0
    tester.circuit.clk_en = 1
    tester.circuit.ASYNCRESET = 0
    tester.step(1)
    tester.circuit.O0.expect(data[0] + data[1])
    tester.circuit.ASYNCRESET = 1
    tester.eval()
    tester.circuit.O0.expect(0)
    tester.step(2)
    tester.circuit.O0.expect(0)
    tester.circuit.ASYNCRESET = 0
    tester.step(2)
    tester.circuit.O0.expect(data[0] + data[1])
    tester.compile_and_run("verilator", flags=["-Wno-UNUSED"],
                           directory="tests/build")
