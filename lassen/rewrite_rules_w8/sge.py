from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def sge_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class sge(Peak):
        def __call__(self, in0: Data, in1: Data) -> Bit:

            return Bit(SInt(in1) >= SInt(in0))

    return sge
