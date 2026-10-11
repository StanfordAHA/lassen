from peak import Peak, family_closure
from peak import family
from peak.family import AbstractFamily

@family_closure
def addshr_fc(family: AbstractFamily):
    Data = family.BitVector[64]
    UInt = family.Unsigned[64]
    @family.assemble(locals(), globals())
    class addshr(Peak):

        def __call__(self, in0: Data, in1: Data, in2: Data) -> Data:
            return Data(UInt(in1) + UInt(in0)) >> in2

    return addshr
