from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def lshr_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class lshr(Peak):
        def __call__(self, in0: Data, in1: Data) -> Data:

            return Data(UInt(in1) >> UInt(in0))

    return lshr
