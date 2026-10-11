from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def abs_fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Unsigned[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class abs(Peak):
        def __call__(self, in0: Data) -> Data:

            return Data((SInt(in0) >= SInt(0)).ite(SInt(in0), SInt(-1) * SInt(in0)))

    return abs
