import lassen.asm as asm
from lassen import PE_fc, Inst_fc
from lassen.common import DATAWIDTH, BFloat16_fc
import random
import os
from rtl_utils import tester, assembler, copy_file, test_dir
from peak.family import PyFamily


Inst = Inst_fc(PyFamily())
Mode_t = Inst.rega

PE = PE_fc(PyFamily())
pe = PE()

BFloat16 = BFloat16_fc(PyFamily())
DataRandom = lambda: PyFamily().BitVector.random(DATAWIDTH)
BitRandom = lambda: random.randint(0, 1)
Data = PyFamily().BitVector[DATAWIDTH]
Bit = PyFamily().Bit
def print_(tester):
    tester.print("#")
    sigs = [
        "ASYNCRESET",
        "CLK",
        "O0",
        "O1",
        "O2",
        "bit0",
        "bit1",
        "bit2",
        "clk_en",
        "config_addr",
        "config_data",
        "config_en",
        "data0",
        "data1",
        "inst",
    ]
    for sig in sigs:
        tester.print(f"({sig}=%x)", getattr(tester.circuit, sig))


def test_vcd(op, N):
    def eval_():
        tester.eval()
        print_(tester)
    tester.clear()
    tester.circuit.ASYNCRESET = 0
    eval_()
    tester.circuit.ASYNCRESET = 1
    eval_()
    tester.circuit.ASYNCRESET = 0
    eval_()
    tester.circuit.inst = assembler(op)
    tester.circuit.CLK = 0
    tester.circuit.clk_en = 1
    tester.circuit.config_en = 0
    eval_()
    N = 4
    for i in range(N):
        tester.circuit.CLK = 1
        eval_()
        tester.circuit.CLK = 0
        tester.circuit.data0 = DataRandom()
        tester.circuit.data1 = DataRandom()
        tester.circuit.bit0 = BitRandom()
        tester.circuit.bit1 = BitRandom()
        tester.circuit.bit2 = BitRandom()
        eval_()
    libs = ["DW_fp_mult.v", "DW_fp_add.v"]
    for filename in libs:
        copy_file(os.path.join("stubs", filename), os.path.join(test_dir, filename))
    tester.compile_and_run(target="verilator",
                           directory=test_dir,
                           flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
                           skip_compile=True,
                           skip_verilator=False)

#asm.or_()
#asm.xor()
#asm.add()
#asm.sub()
#asm.lsl()
#asm.lsr()
#asm.umin()
#asm.umax()
test_vcd(op = asm.and_(), N=1000)
