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
def bit8_unpack_high_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    BitVector = family.BitVector

    @family.assemble(locals(), globals())
    class bit8_unpack_high(Peak):
        def __call__(self, in0: Data) -> Data:
            # Extract bits [15:8] and zero-extend to 16 bits
            high8 = BitVector[8](in0[8:16])
            return BitVector[16](high8)

    return bit8_unpack_high