from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def bit_or_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class bit_or(Peak):
        def __call__(self, in1: Bit, in0: Bit) -> Bit:

            return Bit(Bit(in0) | Bit(in1))

    return bit_or
