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
def int2f_unpack_low_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    SInt = family.Signed
    UInt = family.Unsigned[16]
    BitVector = family.BitVector
    Bit = family.Bit

    # Get the BFloat16 type.
    BFloat16 = BFloat16_fc(family)

    @family.assemble(locals(), globals())
    class int2f_unpack_low(Peak):
        def __call__(self, in0: Data) -> Data:
            # Extract lower 8 bits as int8
            int8_val = SInt[16](BitVector[8](in0[0:8]))

            # Convert int8 to bfloat16 using fp_cnvint2f logic
            if int8_val < 0:
                sign = BitVector[16](0x8000)
                abs_input = BitVector[16](-SInt[16](int8_val))
            else:
                sign = BitVector[16](0)
                abs_input = BitVector[16](int8_val)
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

    return int2f_unpack_low