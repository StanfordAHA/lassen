from lassen.mem import *
import lassen.mem.asm as asm
from hwtypes import BitVector, Bit
import coreir
import metamapper as mm
import pytest

family = BitVector.get_family()
MemInstr, (Rom, Fifo, LineBuffer) = gen_mem_instr(family,width,depth)
Data = BitVector[width]
Mem = gen_mem(family)
def test_rom():

    #Load addr 0 with Data(0), addr 1 with Data(1), etc...
    instr = asm.rom([i for i in range(depth)])
    mem = Mem()
    for i in range(depth):
        #                addr    din         
        assert mem(instr,Data(i),Data(0)) == Data(i)

