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
def fp_cnvint2f_fc(family: AbstractFamily):
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
    class fp_cnvint2f(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:

            sign = BitVector[16](0)
            if sign[15] == Bit(1):
                abs_input = BitVector[16](-SInt[16](in0))
            else:
                abs_input = BitVector[16](in0)
            scale = SInt[16](-127)
            # for bit_pos in range(8):
            #   if (abs_exp[bit_pos]==Bit(1)):
            #     scale = bit_pos
            if abs_input[0] == Bit(1):
                scale = SInt[16](0)
            if abs_input[1] == Bit(1):
                scale = SInt[16](1)
            if abs_input[2] == Bit(1):
                scale = SInt[16](2)
            if abs_input[3] == Bit(1):
                scale = SInt[16](3)
            if abs_input[4] == Bit(1):
                scale = SInt[16](4)
            if abs_input[5] == Bit(1):
                scale = SInt[16](5)
            if abs_input[6] == Bit(1):
                scale = SInt[16](6)
            if abs_input[7] == Bit(1):
                scale = SInt[16](7)
            if abs_input[8] == Bit(1):
                scale = SInt[16](8)
            if abs_input[9] == Bit(1):
                scale = SInt[16](9)
            if abs_input[10] == Bit(1):
                scale = SInt[16](10)
            if abs_input[11] == Bit(1):
                scale = SInt[16](11)
            if abs_input[12] == Bit(1):
                scale = SInt[16](12)
            if abs_input[13] == Bit(1):
                scale = SInt[16](13)
            if abs_input[14] == Bit(1):
                scale = SInt[16](14)
            if abs_input[15] == Bit(1):
                scale = SInt[16](15)
            normmant_mul_left = SInt[16](abs_input)
            normmant_mul_right = SInt[16](15) - scale
            normmant_mask = SInt[16](0x7F00)

            # if (alu == ALU_t.FCnvInt2F) | (alu == ALU_t.FCnvExp2F):
            if scale >= 0:
                normmant = BitVector[16](
                    (normmant_mul_left << normmant_mul_right) & normmant_mask
                )
            else:
                normmant = BitVector[16](0)

            normmant = BitVector[16](normmant) >> 8

            biased_scale = scale + 127
            to_float_result = (
                sign | ((BitVector[16](biased_scale) << 7) & (0xFF << 7)) | normmant
            )

            return to_float_result

    return fp_cnvint2f
