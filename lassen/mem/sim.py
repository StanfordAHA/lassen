from hwtypes import TypeFamily
from peak import Peak, name_outputs, PeakNotImplementedError
from .isa import *

width = 16
depth = 1024

def gen_mem(family, width=width,depth=depth):
    MemInstr = gen_mem_instr(family,width,depth)
    Rom = MemInstr.field_dict['Rom']
    Bit = family.Bit
    Data = family.BitVector[width]

    class Mem(Peak):
        def __init__(self):
            pass
            #self.mem = RAM(Word, depth, [Data(0) for i in range(depth)])

        #TODO For now only define the ports relevant for the ROM
        @name_outputs(rdata=Data)
        def __call__(self,instr : MemInstr, ain : Data, din : Data):

            instr_kind, instr = instr.match()
            if instr_kind == Rom:
                ain_int = int(ain)
                if ain_int >= depth:
                    raise ValueError("address out of range!")
                return instr.init[ain_int]
            else:
                raise PeakNotImplementedError("NYI")
    return Mem
