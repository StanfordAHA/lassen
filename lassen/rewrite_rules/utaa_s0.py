from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def utaa_s0_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class utaa_s0(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data((UInt(in0) + UInt(in1)) + UInt(in2))

    return utaa_s0
