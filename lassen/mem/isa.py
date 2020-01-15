from hwtypes import BitVector, Bit
from hwtypes.adt import Sum, Enum, Product, Tuple
import magma as m
from functools import lru_cache

@lru_cache()
def gen_mem_instr(family, width, depth):

    class Fifo(Product):
        pass

    class LineBuffer(Product):
        pass

    class Rom(Product):
        init=Tuple[(family.BitVector[width] for _ in range(depth))]

    class MemInstr(Sum[Rom, Fifo, LineBuffer]):
        pass

    return MemInstr, (Rom, Fifo, LineBuffer)
