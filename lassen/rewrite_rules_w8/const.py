from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def const_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class const(Peak):
        def __call__(self, in0: Const(Data)) -> Data:

            return in0

    return const
