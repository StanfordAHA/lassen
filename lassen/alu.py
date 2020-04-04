from peak import Peak, name_outputs, family_closure
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH, BFloat16_fc
from hwtypes.adt import Enum
import random
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
    FGetMant = 0x92
    FAddIExp = 0x93
    FSubExp = 0x94
    FCnvExp2F = 0x95
    FGetFInt = 0x96
    FGetFFrac = 0x97
    FCnvInt2F = 0x98

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
        def __call__(self, alu: ALU_t, signed_: Signed_t, a: Data, b: Data, d:Bit) -> (Data, Bit, Bit, Bit, Bit, Bit):
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
            const = int(random.random() * 2**16)
            #if alu != ALU.Mult0:
            #    mula = 0
            #    mulb = 0
            mul = mula * const
            #a_inf = fp_is_inf(a)
            #b_inf = fp_is_inf(b)
            #a_neg = fp_is_neg(a)
            #b_neg = fp_is_neg(b)

            #if alu == ALU_t.FCnvExp2F:
            #    expa0 = BitVector[8](a[7:15])
            #    biased_exp0 = SInt[9](expa0.zext(1))
            #    unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            #    if (unbiased_exp0 < 0):
            #        sign = BitVector[16](0x8000)
            #        abs_exp0 = -unbiased_exp0
            #    else:
            #        sign = BitVector[16](0x0000)
            #        abs_exp0 = unbiased_exp0
            #    abs_exp = BitVector[8](abs_exp0[0:8])
            #    scale = SInt[16](-127)
            #    # for bit_pos in range(8):
            #    #   if (abs_exp[bit_pos]==Bit(1)):
            #    #     scale = bit_pos
            #    if (abs_exp[0] == Bit(1)):
            #        scale = SInt[16](0)
            #    if (abs_exp[1] == Bit(1)):
            #        scale = SInt[16](1)
            #    if (abs_exp[2] == Bit(1)):
            #        scale = SInt[16](2)
            #    if (abs_exp[3] == Bit(1)):
            #        scale = SInt[16](3)
            #    if (abs_exp[4] == Bit(1)):
            #        scale = SInt[16](4)
            #    if (abs_exp[5] == Bit(1)):
            #        scale = SInt[16](5)
            #    if (abs_exp[6] == Bit(1)):
            #        scale = SInt[16](6)
            #    if (abs_exp[7] == Bit(1)):
            #        scale = SInt[16](7)
            #    normmant_mul_left = SInt[16](abs_exp)
            #    normmant_mul_right = SInt[16](1) << (SInt[16](7)-scale)
            #    normmant_mask = SInt[16](0x7F)
            #else: #alu == ALU_t.FCnvInt2F:
            #    if signed_ == Signed_t.signed:
            #        sign = BitVector[16]((a) & 0x8000)
            #    else:
            #        sign = BitVector[16](0)
            #    if (sign[15] == Bit(1)):
            #        abs_input = BitVector[16](-SInt[16](a))
            #    else:
            #        abs_input = BitVector[16](a)
            #    scale = SInt[16](-127)
            #    # for bit_pos in range(8):
            #    #   if (abs_exp[bit_pos]==Bit(1)):
            #    #     scale = bit_pos
            #    if (abs_input[0] == Bit(1)):
            #        scale = SInt[16](0)
            #    if (abs_input[1] == Bit(1)):
            #        scale = SInt[16](1)
            #    if (abs_input[2] == Bit(1)):
            #        scale = SInt[16](2)
            #    if (abs_input[3] == Bit(1)):
            #        scale = SInt[16](3)
            #    if (abs_input[4] == Bit(1)):
            #        scale = SInt[16](4)
            #    if (abs_input[5] == Bit(1)):
            #        scale = SInt[16](5)
            #    if (abs_input[6] == Bit(1)):
            #        scale = SInt[16](6)
            #    if (abs_input[7] == Bit(1)):
            #        scale = SInt[16](7)
            #    if (abs_input[8] == Bit(1)):
            #        scale = SInt[16](8)
            #    if (abs_input[9] == Bit(1)):
            #        scale = SInt[16](9)
            #    if (abs_input[10] == Bit(1)):
            #        scale = SInt[16](10)
            #    if (abs_input[11] == Bit(1)):
            #        scale = SInt[16](11)
            #    if (abs_input[12] == Bit(1)):
            #        scale = SInt[16](12)
            #    if (abs_input[13] == Bit(1)):
            #        scale = SInt[16](13)
            #    if (abs_input[14] == Bit(1)):
            #        scale = SInt[16](14)
            #    if (abs_input[15] == Bit(1)):
            #        scale = SInt[16](15)
            #    normmant_mul_left = SInt[16](abs_input)
            #    normmant_mul_right = (SInt[16](1) << (SInt[16](15)-scale))
            #    normmant_mask = SInt[16](0x7f00)

            ##if (alu == ALU_t.FCnvInt2F) | (alu == ALU_t.FCnvExp2F):
            #if (scale >= 0):
            #    normmant = BitVector[16](
            #        (normmant_mul_left * normmant_mul_right) & normmant_mask)
            #else:
            #    normmant = BitVector[16](0)

            #if alu == ALU_t.FCnvInt2F:
            #    normmant = BitVector[16](normmant) >> 8

            #biased_scale = scale + 127
            #to_float_result = (sign | ((BitVector[16](biased_scale) << 7) & (
            #        0xFF << 7)) | normmant)

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
            # this is now a MAC
            elif alu == ALU_t.Mult0:
                res, C, V = mul[:16] + b, Bit(0), Bit(0)  # wrong C, V
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
                res, res_p = abs_pred.ite(a, -SInt[16](a)), Bit(a[-1])
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
            #elif (alu == ALU_t.FP_add) | (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_cmp):
            #    #Flip the sign bit of b
            #    if (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_cmp):
            #        b = (Data(1) << (DATAWIDTH-1)) ^ b
            #    a_fpadd = bv2float(a)
            #    b_fpadd = bv2float(b)
            #    res = float2bv(a_fpadd + b_fpadd)
            #    res_p = Bit(0)
            #elif alu == ALU_t.FP_mult:
            #    a_fpmul = bv2float(a)
            #    b_fpmul = bv2float(b)
            #    res = float2bv(a_fpmul * b_fpmul)
            #    res_p = Bit(0)
            #elif alu == ALU_t.FGetMant:
            #    res, res_p = (a & 0x7F), Bit(0)
            #elif alu == ALU_t.FAddIExp:
            #    sign = BitVector[16]((a & 0x8000))
            #    exp = UData(a)[7:15]
            #    exp_check = exp.zext(1)
            #    exp = exp + UData(b)[0:8]
            #    exp_check = exp_check + UData(b)[0:9]
            #    # Augassign not supported by magma yet
            #    # exp += SInt[8](b[0:8])
            #    # exp_check += SInt[9](b[0:9])
            #    exp_shift = BitVector[16](exp)
            #    exp_shift = exp_shift << 7
            #    mant = BitVector[16]((a & 0x7F))
            #    res, res_p = (sign | exp_shift | mant), (exp_check > 255)
            #elif alu == ALU_t.FSubExp:
            #    signa = BitVector[16]((a & 0x8000))
            #    expa = UData(a)[7:15]
            #    signb = BitVector[16]((b & 0x8000))
            #    expb = UData(b)[7:15]
            #    expa = (expa - expb + 127)
            #    exp_shift = BitVector[16](expa)
            #    exp_shift = exp_shift << 7
            #    manta = BitVector[16]((a & 0x7F))
            #    res, res_p = ((signa | signb) | exp_shift | manta), Bit(0)
            #elif alu == ALU_t.FCnvExp2F:
            #    res, res_p = to_float_result, Bit(0)
            #elif alu == ALU_t.FGetFInt:
            #    signa = BitVector[16]((a & 0x8000))
            #    manta = BitVector[16]((a & 0x7F)) | 0x80
            #    expa0 = UData(a)[7:15]
            #    biased_exp0 = SInt[9](expa0.zext(1))
            #    unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            #    if (unbiased_exp0 < 0):
            #        manta_shift0 = BitVector[23](0)
            #    else:
            #        manta_shift0 = BitVector[23](
            #            manta) << BitVector[23](unbiased_exp0)
            #    unsigned_res0 = BitVector[23](manta_shift0 >> BitVector[23](7))
            #    unsigned_res = BitVector[16](unsigned_res0[0:16])
            #    if (signa == 0x8000):
            #        signed_res = -SInt[16](unsigned_res)
            #    else:
            #        signed_res = SInt[16](unsigned_res)
            #    # We are not checking for overflow when converting to int
            #    res, res_p, V = signed_res, Bit(0), (expa0 >  BitVector[8](142))
            #elif alu == ALU_t.FGetFFrac:
            #    signa = BitVector[16]((a & 0x8000))
            #    manta = BitVector[16]((a & 0x7F)) | 0x80
            #    expa0 = BitVector[8](a[7:15])
            #    biased_exp0 = SInt[9](expa0.zext(1))
            #    unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))

            #    if (unbiased_exp0 < 0):
            #        manta_shift1 = BitVector[16](
            #            manta) >> BitVector[16](-unbiased_exp0)
            #    else:
            #        manta_shift1 = BitVector[16](
            #            manta) << BitVector[16](unbiased_exp0)
            #    unsigned_res = BitVector[16]((manta_shift1 & 0x07F))
            #    if (signa == 0x8000):
            #        signed_res = -SInt[16](unsigned_res)
            #    else:
            #        signed_res = SInt[16](unsigned_res)

            #    # We are not checking for overflow when converting to int
            #    res, res_p = signed_res, Bit(0)
            #else: #alu == ALU_t.FCnvInt2F:
            #    res, res_p = to_float_result, Bit(0)

            ## else:
            ##    raise NotImplementedError(alu)

            #N = Bit(res[-1])
            #if (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_add) | (alu == ALU_t.FP_mult) | (alu==ALU_t.FP_cmp):
            #    Z = fp_is_zero(res)
            #else:
            #    Z = (res == SData(0))

            ##Nicely handles infinities for comparisons
            #if (alu == ALU_t.FP_cmp):
            #    if (a_inf & b_inf) & (a_neg == b_neg):
            #        Z = Bit(1)

            Z = (res == 0)
            N = Bit(res[-1])
            return res, res_p, Z, N, C, V

    return ALU
