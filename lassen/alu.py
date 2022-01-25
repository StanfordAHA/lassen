from peak import Peak, name_outputs, family_closure, Const
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH, BFloat16_fc
from hwtypes.adt import Enum
import magma as m
import os
import pathlib
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
    FP_add = 0x16
    FP_sub = 0x17
    FP_cmp = 0x18
    FP_mult = 0x19
    FP_div = 0x20
    FP_ln = 0x21
    FP_exp = 0x22
    FP_sin = 0x23

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

lassen_home = pathlib.Path(__file__).parent.resolve()
custom_ops = {}
for op in ["div", "ln", "exp", "sin"]:
    f = f"{lassen_home}/{op}.v"
    assert os.path.exists(f)
    custom_ops[op] = m.define_from_verilog_file(f)[0]

@family_closure
def ALU_fc(family):

    BitVector = family.BitVector
    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit
    SInt = family.Signed
    SData = SInt[DATAWIDTH]
    UInt = family.Unsigned
    UData = UInt[DATAWIDTH]
    UData32 = UInt[32]

    BFloat16 = BFloat16_fc(family)
    FPExpBV = family.BitVector[8]
    FPFracBV = family.BitVector[7]

    def bv2float(bv):
        return BFloat16.reinterpret_from_bv(bv)

    def float2bv(bvf):
        return BFloat16.reinterpret_as_bv(bvf)

    def fp_get_exp(val : Data):
        return val[7:15]

    def fp_get_frac(val : Data):
        return val[:7]

    def fp_is_zero(val : Data):
        return (fp_get_exp(val) == FPExpBV(0)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_inf(val : Data):
        return (fp_get_exp(val) == FPExpBV(-1)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_neg(val : Data):
        return Bit(val[-1])

    @family.assemble(locals(), globals())
    class ALU(Peak):
        #@name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
        def __call__(self, alu: Const(ALU_t), signed_: Const(Signed_t), a: Data, b: Data, d:Bit) -> (Data, Bit, Bit, Bit, Bit, Bit):
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
                abs_pred = a_u >= SData(0)
                shr = Data(a_u >> b_u)
            mul = mula * mulb
            a_inf = fp_is_inf(a)
            b_inf = fp_is_inf(b)
            a_neg = fp_is_neg(a)
            b_neg = fp_is_neg(b)

            Cin = Bit(0)
            if (alu == ALU_t.Sub) | (alu == ALU_t.Sbc):
                b = ~b
            if (alu == ALU_t.Sub):
                Cin = Bit(1)
            elif (alu == ALU_t.Adc) | (alu == ALU_t.Sbc):
                Cin = d

            C = Bit(0)
            V = Bit(0)
            if (alu == ALU_t.Add) | (alu == ALU_t.Sub) | (alu == ALU_t.Adc) | (alu == ALU_t.Sbc):
                #adc needs to be unsigned
                res, C = UData(a).adc(UData(b), Cin)
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
            elif (alu == ALU_t.FP_add) | (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_cmp):
                #Flip the sign bit of b
                if (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_cmp):
                    b = (Data(1) << (DATAWIDTH-1)) ^ b
                a_fpadd = bv2float(a)
                b_fpadd = bv2float(b)
                res = float2bv(a_fpadd + b_fpadd)
                res_p = Bit(0)
            elif alu == ALU_t.FP_mult:
                a_fpmul = bv2float(a)
                b_fpmul = bv2float(b)
                res = float2bv(a_fpmul * b_fpmul)
                res_p = Bit(0)
            elif alu == ALU_t.FP_div:
                res = custom_ops["div"]()(a, b)
                res_p = Bit(0)
            elif alu == ALU_t.FP_ln:
                res = custom_ops["ln"]()(a)
                res_p = Bit(0)
            elif alu == ALU_t.FP_exp:
                res = custom_ops["exp"]()(a)
                res_p = Bit(0)
            elif alu == ALU_t.FP_sin:
                res = custom_ops["sin"]()(a)
                res_p = Bit(0)
            else: #alu == ALU_t.FCnvInt2F:
                res, res_p = 0, Bit(0)

            # else:
            #    raise NotImplementedError(alu)

            N = Bit(res[-1])
            if (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_add) | (alu == ALU_t.FP_mult) | (alu==ALU_t.FP_cmp):
                Z = fp_is_zero(res)
            else:
                Z = (res == SData(0))

            #Nicely handles infinities for comparisons
            if (alu == ALU_t.FP_cmp):
                if (a_inf & b_inf) & (a_neg == b_neg):
                    Z = Bit(1)

            return res, res_p, Z, N, C, V

    return ALU
