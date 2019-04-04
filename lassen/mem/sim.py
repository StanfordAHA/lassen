from hwtypes import TypeFamily
from peak import Peak, name_outputs
import peak.adt
from .isa import*

def gen_mem(family, width=16,depth=1024):
    MemInstr = gen_mem_instr(family,width,depth)
    
    Bit = family.Bit
    Data = family.BitVector[DATAWIDTH]

    class Mem(Peak):
        def __init__(self):
            pass

        @name_outputs(rdata=Data,valid=Bit,almost_full=Bit)
        def __call__(self,instr : MemInstr, ain : Data, ren : Bit, din : Data, wen : Bit):
            return Data(0),Bit(0),Bit(0)

