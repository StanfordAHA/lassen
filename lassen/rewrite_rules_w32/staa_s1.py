from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def staa_s1_fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Unsigned[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class staa_s1(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data(SInt(in1) + (SInt(in2) + SInt(in0)))

    return staa_s1
