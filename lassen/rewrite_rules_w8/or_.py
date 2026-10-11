from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def or__fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class or_(Peak):
        def __call__(self, in1: Data, in0: Data) -> Data:

            return Data(UInt(in0) | UInt(in1))

    return or_
