from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def bit_xor_fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Unsigned[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class bit_xor(Peak):
        def __call__(self, in1: Bit, in0: Bit) -> Bit:

            return Bit(Bit(in0) ^ Bit(in1))

    return bit_xor
