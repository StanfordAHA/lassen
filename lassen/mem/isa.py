from hwtypes import BitVector, Bit
from peak.adt import Enum, Product
import magma as m
from functools import lru_cache

width = 16
depth = 1024

def gen_mem_init(family,width=16,depth=1024):
    arrdata = [family.BitVector[width] for _ in range(depth)]
    class MemInit(family.Tuple[arrdata]):
        pass
    return MemInit

def gen_mem_mode(family):
    class MemMode(family.Enum):
        Ram = 0
        Fifo = 1
        Linebuffer = 2
    return MemMode

def gen_mem_instr(family,width=16,depth=1024):
    MemMode = gen_mem_mode(family)
    MemInit = gen_mem_init(family,width,depth)

    class MemInstr(family.Product):
        mode : MemMode
        init : MemInit
        need_init : family.Bit
    return MemInstr


