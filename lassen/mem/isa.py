from hwtypes import BitVector, Bit
from hwtypes.adt import TaggedUnion, Product, Tuple
import magma as m
from functools import lru_cache

@lru_cache()
def gen_mem_instr(width, depth):

    class Fifo(Product):
        pass

    class LineBuffer(Product):
        pass

    class Rom(Product):
        init=Tuple[(BitVector[width] for _ in range(depth))]

    class MemInstr(TaggedUnion, cache=True):
        rom=Rom
        fifo=Fifo
        lb=LineBuffer

    return MemInstr
