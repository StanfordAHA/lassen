from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def shl_fc(family: AbstractFamily):
    Data = family.BitVector[64]
    Data32 = family.Unsigned[128]
    SInt = family.Signed[64]
    UInt = family.Unsigned[64]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class shl(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:

            return Data(SInt(in1) << SInt(in0))

    return shl
