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
def f2int_pack_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    SInt = family.Signed
    UInt = family.Unsigned[16]
    BitVector = family.BitVector
    Bit = family.Bit

    # Get the BFloat16 type.
    BFloat16 = BFloat16_fc(family)

    @family.assemble(locals(), globals())
    class f2int_pack(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:
            # Convert in0 from bf16 to int8
            sign_a = BitVector[16](in0 & 0x8000)
            mant_a = BitVector[16](in0 & 0x7F) | 0x80
            exp_a = UInt(in0)[7:15]
            biased_exp_a = SInt[9](exp_a.zext(1))
            unbiased_exp_a = SInt[9](biased_exp_a - SInt[9](127))
            if unbiased_exp_a < 0:
                mant_shift_a = BitVector[23](0)
            else:
                mant_shift_a = BitVector[23](mant_a) << BitVector[23](unbiased_exp_a)
            unsigned_res0_a = BitVector[23](mant_shift_a >> BitVector[23](7))
            unsigned_res_a = BitVector[8](unsigned_res0_a[0:8])
            if sign_a == 0x8000:
                int8_a = -SInt[8](unsigned_res_a)
            else:
                int8_a = SInt[8](unsigned_res_a)

            # Convert in1 from bf16 to int8
            sign_b = BitVector[16](in1 & 0x8000)
            mant_b = BitVector[16](in1 & 0x7F) | 0x80
            exp_b = UInt(in1)[7:15]
            biased_exp_b = SInt[9](exp_b.zext(1))
            unbiased_exp_b = SInt[9](biased_exp_b - SInt[9](127))
            if unbiased_exp_b < 0:
                mant_shift_b = BitVector[23](0)
            else:
                mant_shift_b = BitVector[23](mant_b) << BitVector[23](unbiased_exp_b)
            unsigned_res0_b = BitVector[23](mant_shift_b >> BitVector[23](7))
            unsigned_res_b = BitVector[8](unsigned_res0_b[0:8])
            if sign_b == 0x8000:
                int8_b = -SInt[8](unsigned_res_b)
            else:
                int8_b = SInt[8](unsigned_res_b)

            # Pack the two int8 values into one 16-bit BitVector
            packed = SInt[16]((BitVector[16](int8_a) << BitVector[16](8)) | BitVector[16](int8_b))
            return packed

    return f2int_pack
