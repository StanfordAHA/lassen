from hwtypes import BitVector
from lassen import gen_pe, asm
from peak import Peak

def gen_Add32(family):
    Data16 = family.BitVector[16]
    Data32 = family.BitVector[32]
    PE = gen_pe(family)
    class Add32(Peak):
        def __init__(self):
            self.pe_lsb = PE()
            self.pe_msb = PE()

        def __call__(self,in0 : Data32, in1 : Data32):
            inst_lsb = asm.inst(asm.ALU.Add,cond=asm.Cond.C)
            inst_msb = asm.add(enable_cin=True)
            lsb,cout,_ = self.pe_lsb(inst_lsb,data0=in0[:16],data1=in1[:16])
            msb,_,_ = self.pe_msb(inst_msb,data0=in0[16:],data1=in1[16:],bit0=cout)
            return Data32.concat(msb,lsb)
    return Add32
