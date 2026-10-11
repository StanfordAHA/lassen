from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def muladd_s1_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class muladd_s1(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data(UInt(in1) + (UInt(in2) * UInt(in0)))

    return muladd_s1
