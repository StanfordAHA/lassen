from hwtypes import TypeFamily
from peak import Peak, name_outputs, PeakNotImplementedError
from .isa import *


width = 16
depth = 1024


def gen_mem(family, width=width, depth=depth):
    MemInstr = gen_mem_instr(family, width, depth)
    Rom = MemInstr.field_dict['Rom']
    Bit = family.Bit
    Data = family.BitVector[width]
    Addr = family.BitVector[width]
    ConfigWidth = family.BitVector[32]

    class Mem(Peak):
        def __init__(self):
            pass
            # self.mem = RAM(Word, depth, [Data(0) for i in range(depth)])

        # TODO For now only define the ports relevant for the ROM
        @name_outputs(rdata=Data)
        def __call__(self, instr: MemInstr, clk_en: Bit, flush: Bit,
                     addr_in: Addr, data_in: Data, data_out: Data,
                     wen_in: Bit, ren_in: Bit, valid_out: Bit,
                     chain_in: Data, chain_out: Data, chain_wen_in: Bit,
                     chain_valid_out: Bit, almost_full: Bit, almost_empty: Bit,
                     switch_db: Bit, config_addr: ConfigWidth,
                     config_data: ConfigWidth, config_read: Bit,
                     config_write: Bit, config_en_sram: BitVector[4],
                     read_data_sram_0: ConfigWidth,
                     read_data_sram_1: ConfigWidth,
                     read_data_sram_2: ConfigWidth,
                     read_data_sram_3: ConfigWidth):

            instr_kind, instr = instr.match()
            if instr_kind == Rom:
                ain_int = int(addr_in)
                if ain_int >= depth:
                    raise ValueError("address out of range!")
                return instr.init[ain_int]
            else:
                raise PeakNotImplementedError("NYI")
    return Mem
