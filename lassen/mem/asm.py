from .isa import *
from .sim import width, depth
from hwtypes import BitVector

Data = BitVector[width]
MemInstr = gen_mem_instr(BitVector.get_family(),width,depth)
Rom = MemInstr.field_dict['Rom']

def rom(init):
    assert len(init)==depth
    instr = MemInstr(Rom(init=Rom.init(*(Data(val) for val in init))))
    return instr
