from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def fp_mux_fc(family: AbstractFamily):
    Data = family.BitVector[64]
    Data32 = family.Unsigned[128]
    SInt = family.Signed[64]
    UInt = family.Unsigned[64]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class fp_mux(Peak):
        def __call__(self, in0: Data, in1: Data, sel: Bit) -> Data:

            return Data(sel.ite(UInt(in0), UInt(in1)))

    return fp_mux
