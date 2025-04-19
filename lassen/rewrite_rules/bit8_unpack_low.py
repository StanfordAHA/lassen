from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode

DATAWIDTH = 16

@family_closure
def bit8_unpack_low_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    BitVector = family.BitVector

    @family.assemble(locals(), globals())
    class bit8_unpack_low(Peak):
        def __call__(self, in0: Data) -> Data:
            # Extract bits [7:0] and zero-extend to 16 bits
            low8 = BitVector[8](in0[0:8])
            return BitVector[16](low8)

    return bit8_unpack_low
