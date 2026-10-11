from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def mul_fc(family: AbstractFamily):
    Data = family.BitVector[64]
    Data32 = family.Unsigned[128]
    SInt = family.Signed[64]
    UInt = family.Unsigned[64]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class mul(Peak):
        def __call__(self, in1: Data, in0: Data) -> Data:

            return Data(UInt(in0) * UInt(in1))

    return mul
