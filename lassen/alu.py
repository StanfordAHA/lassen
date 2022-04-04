from peak import Peak, name_outputs, family_closure, Const
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH, BFloat16_fc
from hwtypes.adt import Enum
from hwtypes import BitVector, Bit as BitPy
# simulate the PE ALU
#
#   inputs
#
#   alu is the ALU operations
#   signed is whether the inputs are unsigned or signed
#   a, b - 16-bit operands
#   d - 1-bit operatnd
#
#
#   returns res, res_p, Z, N, C, V
#
#   res - 16-bit result
#   res_p - 1-bit result
#   Z (result is 0)
#   N (result is negative)
#   C (carry generated)
#   V (overflow generated)



class ALU_t(Enum):
    Add = 0
    Sub = 1
    Adc = 2
    Sbc = 6
    Abs = 3
    GTE_Max = 4
    LTE_Min = 5
    Sel = 8
    Mult0 = 0xb
    Mult1 = 0xc
    Mult2 = 0xd
    SHR = 0xf
    SHL = 0x11
    Or = 0x12
    And = 0x13
    XOr = 0x14


"""
Whether the operation is unsigned (0) or signed (1)
"""
class Signed_t(Enum):
    unsigned = 0
    signed = 1

def overflow(a, b, res):
    msb_a = a[-1]
    msb_b = b[-1]
    N = res[-1]
    return (msb_a & msb_b & ~N) | (~msb_a & ~msb_b & N)

@family_closure
def ALU_fc(family):

    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit
    SInt = family.Signed
    SData = SInt[DATAWIDTH]
    UInt = family.Unsigned
    UData = UInt[DATAWIDTH]
    UData32 = UInt[32]

    DataPy = BitVector[DATAWIDTH]


    @family.assemble(locals(), globals(), set_port_names=True)
    class ALU(Peak):
        @name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
        def __call__(self, alu: Const(ALU_t), signed_: Const(Signed_t), a: DataPy, b: DataPy, d: BitPy) -> (DataPy, BitPy, BitPy, BitPy, BitPy, BitPy):
            if signed_ == Signed_t.signed:
                a_s = SData(a)
                b_s = SData(b)
                mula, mulb = UData32(a_s.sext(16)), UData32(b_s.sext(16))
                gte_pred = a_s >= b_s
                lte_pred = a_s <= b_s
                abs_pred = a_s >= SData(0)
                shr = Data(a_s >> b_s)
            else: #signed_ == Signed_t.unsigned:
                a_u = UData(a)
                b_u = UData(b)
                mula, mulb = a_u.zext(16), b_u.zext(16)
                gte_pred = a_u >= b_u
                lte_pred = a_u <= b_u
                abs_pred = Bit(1) # a_u >= UData(0)
                shr = Data(a_u >> b_u)
            mul = mula * mulb

            Cin = Bit(0)
            if (alu == ALU_t.Sub) | (alu == ALU_t.Sbc):
                b = ~b
            if (alu == ALU_t.Sub):
                Cin = Bit(1)
            elif (alu == ALU_t.Adc) | (alu == ALU_t.Sbc):
                Cin = d

            # factor out comman add
            res_tmp, C_tmp = UData(a).adc(UData(b), Cin)

            C = Bit(0)
            V = Bit(0)
            res, res_p = Data(0x5555), Bit(0)
            if (alu == ALU_t.Add) | (alu == ALU_t.Sub) | (alu == ALU_t.Adc) | (alu == ALU_t.Sbc):
                #adc needs to be unsigned
                res, C = res_tmp, C_tmp
                V = overflow(a, b, res)
                res_p = C
            elif alu == ALU_t.Mult0:
                res, C, V = mul[:16], Bit(0), Bit(0)  # wrong C, V
                res_p = C
            elif alu == ALU_t.Mult1:
                res, C, V = mul[8:24], Bit(0), Bit(0)  # wrong C, V
                res_p = C
            elif alu == ALU_t.Mult2:
                res, C, V = mul[16:32], Bit(0), Bit(0)  # wrong C, V
                res_p = C
            elif alu == ALU_t.GTE_Max:
                # C, V = a-b?
                res, res_p = gte_pred.ite(a, b), gte_pred
            elif alu == ALU_t.LTE_Min:
                # C, V = a-b?
                res, res_p = lte_pred.ite(a, b), lte_pred
            elif alu == ALU_t.Abs:
                res, res_p = abs_pred.ite(a, UInt[16](-SInt[16](a))), Bit(a[-1])
            elif alu == ALU_t.Sel:
                res, res_p = d.ite(a, b), Bit(0)
            elif alu == ALU_t.And:
                res, res_p = a & b, Bit(0)
            elif alu == ALU_t.Or:
                res, res_p = a | b, Bit(0)
            elif alu == ALU_t.XOr:
                res, res_p = a ^ b, Bit(0)
            elif alu == ALU_t.SHR:
                #res, res_p = a >> Data(b[:4]), Bit(0)
                res, res_p = shr, Bit(0)
            elif alu == ALU_t.SHL:
                #res, res_p = a << Data(b[:4]), Bit(0)
                res, res_p = a << b, Bit(0)

            N = Bit(res[-1])
            Z = (res == SData(0))

            return res, res_p, Z, N, C, V

    return ALU
