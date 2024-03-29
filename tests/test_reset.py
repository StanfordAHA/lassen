from lassen.mode import Mode_t
from lassen.asm import add
from rtl_utils import pe_circuit, assembler, compile_and_run_tester
import magma as m
import fault
import hwtypes


def test_reset():
    tester = fault.Tester(pe_circuit, clock=pe_circuit.CLK)

    inst = add(ra_mode=Mode_t.DELAY, rb_mode=Mode_t.DELAY)
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
    tester.eval()
    tester.step(2)
    tester.circuit.O0.expect(data[0] + data[1])
    tester.circuit.ASYNCRESET = 1
    tester.eval()
    tester.circuit.O0.expect(0)
    tester.step(2)
    tester.circuit.O0.expect(0)
    tester.circuit.ASYNCRESET = 0
    tester.step(2)
    tester.circuit.O0.expect(data[0] + data[1])
    compile_and_run_tester(tester)
