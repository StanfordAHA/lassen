from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def abs_fc(family: AbstractFamily):
    Data = family.BitVector[64]
    Data32 = family.Unsigned[128]
    SInt = family.Signed[64]
    UInt = family.Unsigned[64]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class abs(Peak):
        def __call__(self, in0: Data) -> Data:

            return Data((SInt(in0) >= SInt(0)).ite(SInt(in0), SInt(-1) * SInt(in0)))

    return abs
