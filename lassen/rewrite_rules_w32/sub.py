from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def sub_fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Unsigned[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class sub(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:

            return Data(UInt(in1) - UInt(in0))

    return sub
