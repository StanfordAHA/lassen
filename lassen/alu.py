from hwtypes import BitVector, Bit, SIntVector
from hwtypes.adt import Enum
from peak import Peak
from .common import Data, DATAWIDTH, BFloat16

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

SInt = SIntVector

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

FPExpBV = BitVector[8]
FPFracBV = BitVector[7]

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

def overflow(a, b, res):
    msb_a = a[-1]
    msb_b = b[-1]
    N = res[-1]
    return (msb_a & msb_b & ~N) | (~msb_a & ~msb_b & N)

class ALU(Peak):
    def __call__(self, alu: ALU_t, signed: Signed_t, a:Data, b:Data, d:Bit) -> (Data, Bit, Bit, Bit, Bit, Bit):
        if signed == Signed_t.signed:
            a = SInt[DATAWIDTH](a)
            b = SInt[DATAWIDTH](b)
            mula, mulb = a.sext(16), b.sext(16)
            gte_pred = a >= b
            lte_pred = a <= b
            abs_pred = a >= 0
            shr = a >> b
        elif signed == Signed_t.unsigned:
            mula, mulb = Data(a).zext(16), Data(b).zext(16)
            gte_pred = a >= b
            lte_pred = a <= b
            abs_pred = a >= 0
            shr = a >> b
        mul = mula * mulb
        a_inf = fp_is_inf(a)
        b_inf = fp_is_inf(b)
        a_neg = fp_is_neg(a)
        b_neg = fp_is_neg(b)

        if alu == ALU_t.FCnvExp2F:
            expa0 = BitVector[8](a[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            if (unbiased_exp0 < 0):
                sign = BitVector[16](0x8000)
                abs_exp0 = -unbiased_exp0
            else:
                sign = BitVector[16](0x0000)
                abs_exp0 = unbiased_exp0
            abs_exp = BitVector[8](abs_exp0[0:8])
            scale = SInt[16](-127)
            # for bit_pos in range(8):
            #   if (abs_exp[bit_pos]==Bit(1)):
            #     scale = bit_pos
            if (abs_exp[0] == Bit(1)):
                scale = SInt[16](0)
            if (abs_exp[1] == Bit(1)):
                scale = SInt[16](1)
            if (abs_exp[2] == Bit(1)):
                scale = SInt[16](2)
            if (abs_exp[3] == Bit(1)):
                scale = SInt[16](3)
            if (abs_exp[4] == Bit(1)):
                scale = SInt[16](4)
            if (abs_exp[5] == Bit(1)):
                scale = SInt[16](5)
            if (abs_exp[6] == Bit(1)):
                scale = SInt[16](6)
            if (abs_exp[7] == Bit(1)):
                scale = SInt[16](7)
            normmant_mul_left = SInt[16](abs_exp)
            normmant_mul_right = SInt[16](1) << (SInt[16](7)-scale)
            normmant_mask = SInt[16](0x7F)
        elif alu == ALU_t.FCnvInt2F:
            if signed == Signed_t.signed:
                sign = BitVector[16]((a) & 0x8000)
            else:
                sign = BitVector[16](0)
            if (sign[15] == Bit(1)):
                abs_input = BitVector[16](-a)
            else:
                abs_input = BitVector[16](a)
            scale = SInt[16](-127)
            # for bit_pos in range(8):
            #   if (abs_exp[bit_pos]==Bit(1)):
            #     scale = bit_pos
            if (abs_input[0] == Bit(1)):
                scale = SInt[16](0)
            if (abs_input[1] == Bit(1)):
                scale = SInt[16](1)
            if (abs_input[2] == Bit(1)):
                scale = SInt[16](2)
            if (abs_input[3] == Bit(1)):
                scale = SInt[16](3)
            if (abs_input[4] == Bit(1)):
                scale = SInt[16](4)
            if (abs_input[5] == Bit(1)):
                scale = SInt[16](5)
            if (abs_input[6] == Bit(1)):
                scale = SInt[16](6)
            if (abs_input[7] == Bit(1)):
                scale = SInt[16](7)
            if (abs_input[8] == Bit(1)):
                scale = SInt[16](8)
            if (abs_input[9] == Bit(1)):
                scale = SInt[16](9)
            if (abs_input[10] == Bit(1)):
                scale = SInt[16](10)
            if (abs_input[11] == Bit(1)):
                scale = SInt[16](11)
            if (abs_input[12] == Bit(1)):
                scale = SInt[16](12)
            if (abs_input[13] == Bit(1)):
                scale = SInt[16](13)
            if (abs_input[14] == Bit(1)):
                scale = SInt[16](14)
            if (abs_input[15] == Bit(1)):
                scale = SInt[16](15)
            normmant_mul_left = SInt[16](abs_input)
            normmant_mul_right = (SInt[16](1) << (SInt[16](15)-scale))
            normmant_mask = SInt[16](0x7f00)
        if (alu == ALU_t.FCnvInt2F) | (alu == ALU_t.FCnvExp2F):
            if (scale >= 0):
                normmant = BitVector[16](
                    (normmant_mul_left * normmant_mul_right) & normmant_mask)
            else:
                normmant = BitVector[16](0)

            if alu == ALU_t.FCnvInt2F:
                normmant = BitVector[16](normmant) >> 8

            biased_scale = scale + 127
            to_float_result = (sign | ((BitVector[16](biased_scale) << 7) & (
                    0xFF << 7)) | normmant)

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
            res, C = a.adc(b, Cin)
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
            res, res_p = gte_pred.ite(a,b), gte_pred
        elif alu == ALU_t.LTE_Min:
            # C, V = a-b?
            res, res_p = lte_pred.ite(a,b), lte_pred
        elif alu == ALU_t.Abs:
            res, res_p = abs_pred.ite(a,-a), Bit(a[-1])
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
            a = bv2float(a)
            b = bv2float(b)
            res = float2bv(a + b)
            res_p = Bit(0)
        elif alu == ALU_t.FP_mult:
            a = bv2float(a)
            b = bv2float(b)
            res = float2bv(a * b)
            res_p = Bit(0)
        elif alu == ALU_t.FGetMant:
            res, res_p = (a & 0x7F), Bit(0)
        elif alu == ALU_t.FAddIExp:
            sign = BitVector[16]((a & 0x8000))
            exp = BitVector[16](a)[7:15]
            exp_check = exp.zext(1)
            exp = exp + b[0:8]
            exp_check = exp_check + b[0:9]
            # Augassign not supported by magma yet
            # exp += SInt[8](b[0:8])
            # exp_check += SInt[9](b[0:9])
            exp_shift = BitVector[16](exp)
            exp_shift = exp_shift << 7
            mant = BitVector[16]((a & 0x7F))
            res, res_p = (sign | exp_shift | mant), (exp_check > 255)
        elif alu == ALU_t.FSubExp:
            signa = BitVector[16]((a & 0x8000))
            expa = BitVector[16](a)[7:15]
            signb = BitVector[16]((b & 0x8000))
            expb = BitVector[16](b)[7:15]
            expa = (expa - expb + 127)
            exp_shift = BitVector[16](expa)
            exp_shift = exp_shift << 7
            manta = BitVector[16]((a & 0x7F))
            res, res_p = ((signa | signb) | exp_shift | manta), Bit(0)
        elif alu == ALU_t.FCnvExp2F:
            res, res_p = to_float_result, Bit(0)
        elif alu == ALU_t.FGetFInt:
            signa = BitVector[16]((a & 0x8000))
            manta = BitVector[16]((a & 0x7F)) | 0x80
            expa0 = BitVector[8](a[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            if (unbiased_exp0 < 0):
                manta_shift0 = BitVector[23](0)
            else:
                manta_shift0 = BitVector[23](
                    manta) << BitVector[23](unbiased_exp0)
            unsigned_res0 = BitVector[23](manta_shift0 >> BitVector[23](7))
            unsigned_res = BitVector[16](unsigned_res0[0:16])
            if (signa == 0x8000):
                signed_res = SInt[16](-unsigned_res)
            else:
                signed_res = SInt[16](unsigned_res)
            # We are not checking for overflow when converting to int
            res, res_p, V = signed_res, 0, (expa0 >  BitVector[8](142))
        elif alu == ALU_t.FGetFFrac:
            signa = BitVector[16]((a & 0x8000))
            manta = BitVector[16]((a & 0x7F)) | 0x80
            expa0 = BitVector[8](a[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))

            if (unbiased_exp0 < 0):
                manta_shift1 = BitVector[16](
                    manta) >> BitVector[16](-unbiased_exp0)
            else:
                manta_shift1 = BitVector[16](
                    manta) << BitVector[16](unbiased_exp0)
            unsigned_res = BitVector[16]((manta_shift1 & 0x07F))
            if (signa == 0x8000):
                signed_res = SInt[16](-unsigned_res)
            else:
                signed_res = SInt[16](unsigned_res)

            # We are not checking for overflow when converting to int
            res, res_p = signed_res, Bit(0)
        elif alu == ALU_t.FCnvInt2F:
            res, res_p = to_float_result, Bit(0)

        # else:
        #    raise NotImplementedError(alu)

        N = Bit(res[-1])
        if (alu == ALU_t.FP_sub) | (alu == ALU_t.FP_add) | (alu == ALU_t.FP_mult) | (alu==ALU_t.FP_cmp):
            Z = fp_is_zero(res)
        else:
            Z = (res == 0)

        #Nicely handles infinities for comparisons
        if (alu == ALU_t.FP_cmp):
            if (a_inf & b_inf) & (a_neg == b_neg):
                Z = Bit(1)

        return res, res_p, Z, N, C, V

#    if family.Bit is m.Bit:
#        if use_assembler:
#            bv_fam = gen_pe_type_family(hwtypes.BitVector.get_family())
#            bv_alu = gen_alu_type(bv_fam)
#            bv_signed = gen_signed_type(bv_fam)
#            assemblers = {
#                ALU: (bv_alu, Assembler(bv_alu).assemble),
#                Signed: (bv_signed, Assembler(bv_signed).assemble)
#            }
#            alu = assemble_values_in_func(assemblers, alu, locals(), globals())
#        alu = m.circuit.combinational(alu)

