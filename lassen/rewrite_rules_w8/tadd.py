from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def tadd_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class tadd(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data(UInt(in0) + UInt(in1) + UInt(in2))

    return tadd
