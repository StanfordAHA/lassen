from peak import Peak, family_closure, Const
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode

DATAWIDTH = 16

@family_closure
def bit8_pack_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    BitVector = family.BitVector
    @family.assemble(locals(), globals())
    class bit8_pack(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:
            # Get lower 8 bits from each input
            in0_lower = BitVector[16](in0[0:8])
            in1_lower = BitVector[16](in1[0:8])

            # Create a 16-bit value with in0_lower in upper bits and in1_lower in lower bits
            packed = (in0_lower << BitVector[16](8)) | in1_lower
            return packed

    return bit8_pack
