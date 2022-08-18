from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma


@family_closure
def fp_getmant_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class fp_getmant(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:
            return Data(in0 & 0x7F)

    return fp_getmant
