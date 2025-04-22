from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode


DATAWIDTH = 16

@family_closure
def e8m0_quant_fc(family: AbstractFamily):
    BitVector = family.BitVector
    SInt = family.Signed
    UInt = family.Unsigned[16]
    UInt8 = family.Unsigned[8]
    Data = family.BitVector[16]
    @family.assemble(locals(), globals())
    class e8m0_quant(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:
            signa = BitVector[16](in0 & 0x8000)
            manta = BitVector[16]((in0 & 0x7F)) | 0x80
            expa0 = UInt(in0)[7:15]
            shared_exp = UInt8(in1[0:8])
            biased_exp0 = SInt[9](expa0.zext(1))
            biased_shared_exp = SInt[9](shared_exp.zext(1))
            # Note: biased_shared_exp already contains bias of 127
            unbiased_quant_exp0 = SInt[9](biased_exp0 - biased_shared_exp)
            if unbiased_quant_exp0 < 0:
                manta_shift0 = BitVector[23](manta) >> BitVector[23](-unbiased_quant_exp0)
            else:
                manta_shift0 = BitVector[23](manta) << BitVector[23](unbiased_quant_exp0)

            # Extract the rounding bit
            rounding_bit = (manta_shift0 >> BitVector[23](6)) & BitVector[23](1)
            # Apply rounding by adding the rounding bit to the truncated result
            unsigned_res0 = BitVector[23]((manta_shift0 >> BitVector[23](7)) + rounding_bit)

            unsigned_res8 = BitVector[8](unsigned_res0[0:8])
            if signa == 0x8000:
                signed_res8 = -SInt[8](unsigned_res8)
            else:
                signed_res8 = SInt[8](unsigned_res8)

            res = BitVector[16](signed_res8.zext(8))
            return res

    return e8m0_quant