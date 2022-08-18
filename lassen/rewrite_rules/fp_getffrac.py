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
def fp_getffrac_fc(family: AbstractFamily):
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
    class fp_getffrac(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:
            signa = BitVector[16]((in0 & 0x8000))
            manta = BitVector[16]((in0 & 0x7F)) | 0x80
            expa0 = BitVector[8](in0[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))

            if unbiased_exp0 < 0:
                manta_shift1 = BitVector[16](manta) >> BitVector[16](-unbiased_exp0)
            else:
                manta_shift1 = BitVector[16](manta) << BitVector[16](unbiased_exp0)
            unsigned_res = BitVector[16]((manta_shift1 & 0x07F))
            if signa == 0x8000:
                signed_res = -SInt[16](unsigned_res)
            else:
                signed_res = SInt[16](unsigned_res)

            # We are not checking for overflow when converting to int
            res = signed_res
            return res

    return fp_getffrac
