from hwtypes import BitVector, Bit
from lassen import PE_fc, asm
from lassen.common import DATAWIDTH
from peak import Peak

Data = BitVector[DATAWIDTH]
PE = PE_fc(Bit.get_family())

#This is a complex operation that implements a Fused multiply add
class FMA(Peak):
    def __init__(self):
        self.pe1 = PE()
        self.pe2 = PE()

    def __call__(self,in0 : Data, in1 : Data, in2 : Data):
        inst1 = asm.smult0()
        inst2 = asm.add()
        pe1_out,_,_ = self.pe1(inst1,in0,in1)
        pe2_out,_,_ = self.pe2(inst2,pe1_out,in2)
        return pe2_out
