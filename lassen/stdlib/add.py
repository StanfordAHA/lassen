from hwtypes import BitVector, Bit
from lassen import PE_fc, asm
from peak import Peak


def Add32_fc(family):
    PE = PE_fc(family)
    Data16 = BitVector[16]
    Data32 = BitVector[32]

    class Add32(Peak):
        def __init__(self):
            self.pe_lsb = PE()
            self.pe_msb = PE()

        def __call__(self, in0: Data32, in1: Data32) -> Data32:
            inst_lsb = asm.add(cond=asm.Cond_t.C)
            inst_msb = asm.adc()
            lsb, cout, _, _, _ = self.pe_lsb(inst_lsb, data0=in0[:16], data1=in1[:16])
            msb, _, _, _, _ = self.pe_msb(
                inst_msb, data0=in0[16:], data1=in1[16:], bit0=cout
            )
            return Data32.concat(lsb, msb)

    return Add32


def Sub32_fc(family):
    PE = PE_fc(family)
    Data16 = BitVector[16]
    Data32 = BitVector[32]

    class Sub32(Peak):
        def __init__(self):
            self.pe_lsb = PE()
            self.pe_msb = PE()

        def __call__(self, in0: Data32, in1: Data32) -> Data32:
            inst_lsb = asm.sub(cond=asm.Cond_t.C)
            inst_msb = asm.sbc()
            lsb, cout, _, _, _ = self.pe_lsb(inst_lsb, data0=in0[:16], data1=in1[:16])
            msb, _, _, _, _ = self.pe_msb(
                inst_msb, data0=in0[16:], data1=in1[16:], bit0=cout
            )
            return Data32.concat(lsb, msb)

    return Sub32
