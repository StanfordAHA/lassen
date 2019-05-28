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
        init = Tuple[(family.BitVector[width] for _ in range(depth))]

    class MemInstr(Sum[Rom, Fifo, LineBuffer]):
        # Const Mode Config
        flush_reg_sel = Bit
        flush_reg_value = Bit
        ren_in_reg_sel = Bit
        ren_in_reg_value = Bit
        switch_db_reg_sel = Bit
        switch_db_reg_value = Bit
        wen_in_reg_sel = Bit
        wen_in_reg_value = Bit
        # FIFO + LB
        almost_count = Bit
        circular_en = Bit
        depth = BitVector[13]
        stencil_width = BitVector[32]   # This is actually Mark's valid delay
        # DB stuff
        read_mode = Bit
        arbitrary_addr = Bit
        starting_addr = BitVector[32]
        iter_cnt = BitVector[32]
        dimensionality = BitVector[32]
        stride_0 = BitVector[32]
        stride_1 = BitVector[32]
        stride_2 = BitVector[32]
        stride_3 = BitVector[32]
        stride_4 = BitVector[32]
        stride_5 = BitVector[32]
        stride_6 = BitVector[32]
        stride_7 = BitVector[32]
        range_0 = BitVector[32]
        range_1 = BitVector[32]
        range_2 = BitVector[32]
        range_3 = BitVector[32]
        range_4 = BitVector[32]
        range_5 = BitVector[32]
        range_6 = BitVector[32]
        range_7 = BitVector[32]
        # Chaining
        enable_chain = Bit
        chain_idx = BitVector[4]
        # Tile
        mode = BitVector[2]
        tile_en = Bit

    return MemInstr
