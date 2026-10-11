from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def staa_s0_fc(family: AbstractFamily):
    Data = family.BitVector[64]
    Data32 = family.Unsigned[128]
    SInt = family.Signed[64]
    UInt = family.Unsigned[64]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class staa_s0(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data((SInt(in0) + SInt(in1)) + SInt(in2))

    return staa_s0
