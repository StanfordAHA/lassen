from peak import Peak, name_outputs, PeakNotImplementedError
from .isa import gen_mem_instr
from lassen.common import DATAWIDTH
from hwtypes import BitVector


# FIXME Have memories adhere to family closure
width = 16
depth = 1024
Data = BitVector[DATAWIDTH]


def gen_mem(width=width, depth=depth):
    MemInstr = gen_mem_instr(width, depth)
    Rom = MemInstr.field_dict["rom"]

    class Mem(Peak):
        def __init__(self):
            pass
            # self.mem = RAM(Word, depth, [Data(0) for i in range(depth)])

        # TODO For now only define the ports relevant for the ROM
        @name_outputs(rdata=Data)
        def __call__(self, instr: MemInstr, ain: Data, din: Data):
            if instr[Rom].match:
                ain_int = int(ain)
                if ain_int >= depth:
                    raise ValueError("address out of range!")
                return instr[Rom].value.init[ain_int]
            else:
                raise PeakNotImplementedError("NYI")

    return Mem
