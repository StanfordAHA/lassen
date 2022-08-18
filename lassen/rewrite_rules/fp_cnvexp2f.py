from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode


DATAWIDTH = 16


def BFloat16_fc(family):
    if isinstance(family, MagmaFamily):
        BFloat16 = magma.BFloat[16]
        BFloat16.reinterpret_from_bv = lambda bv: BFloat16(bv)
        BFloat16.reinterpret_as_bv = lambda f: magma.Bits[16](f)
        return BFloat16
    elif isinstance(family, SMTFamily):
        FPV = SMTFPVector
    else:
        FPV = FPVector
    BFloat16 = FPV[8, 7, RoundingMode.RNE, False]
    return BFloat16


@family_closure
def fp_cnvexp2f_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed
    UInt = family.Unsigned[16]
    Bit = family.Bit

    BFloat16 = BFloat16_fc(family)
    FPExpBV = family.BitVector[8]
    FPFracBV = family.BitVector[7]
    BitVector = family.BitVector

    def bv2float(bv):
        return BFloat16.reinterpret_from_bv(bv)

    def float2bv(bvf):
        return BFloat16.reinterpret_as_bv(bvf)

    def fp_get_exp(val: Data):
        return val[7:15]

    def fp_get_frac(val: Data):
        return val[:7]

    def fp_is_zero(val: Data):
        return (fp_get_exp(val) == FPExpBV(0)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_inf(val: Data):
        return (fp_get_exp(val) == FPExpBV(-1)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_neg(val: Data):
        return Bit(val[-1])

    @family.assemble(locals(), globals())
    class fp_cnvexp2f(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:
            expa0 = BitVector[8](in0[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            if unbiased_exp0 < 0:
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
            if abs_exp[0] == Bit(1):
                scale = SInt[16](0)
            if abs_exp[1] == Bit(1):
                scale = SInt[16](1)
            if abs_exp[2] == Bit(1):
                scale = SInt[16](2)
            if abs_exp[3] == Bit(1):
                scale = SInt[16](3)
            if abs_exp[4] == Bit(1):
                scale = SInt[16](4)
            if abs_exp[5] == Bit(1):
                scale = SInt[16](5)
            if abs_exp[6] == Bit(1):
                scale = SInt[16](6)
            if abs_exp[7] == Bit(1):
                scale = SInt[16](7)
            normmant_mul_left = SInt[16](abs_exp)
            normmant_mul_right = SInt[16](7) - scale
            normmant_mask = SInt[16](0x7F)

            if scale >= 0:
                normmant = BitVector[16](
                    (normmant_mul_left << normmant_mul_right) & normmant_mask
                )
            else:
                normmant = BitVector[16](0)

            biased_scale = scale + 127
            to_float_result = (
                sign | ((BitVector[16](biased_scale) << 7) & (0xFF << 7)) | normmant
            )
            return to_float_result

    return fp_cnvexp2f
