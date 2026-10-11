from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def and__fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Unsigned[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class and_(Peak):
        def __call__(self, in1: Data, in0: Data) -> Data:

            return Data(UInt(in0) & UInt(in1))

    return and_
