from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def utss_s0_fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Unsigned[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class utss_s0(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data((UInt(in0) - UInt(in1)) - UInt(in2))

    return utss_s0
