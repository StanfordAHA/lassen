from .isa import *
from .sim import width, depth
from hwtypes import BitVector

Data = BitVector[width]
MemInstr = gen_mem_instr(width, depth)
Rom = MemInstr.field_dict["rom"]


def rom(init):
    assert len(init) == depth
    instr = MemInstr(rom=Rom(init=Rom.init(*(Data(val) for val in init))))
    return instr
