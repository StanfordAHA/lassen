from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def fp_mux_fc(family: AbstractFamily):
    Data = family.BitVector[8]
    Data32 = family.Unsigned[16]
    SInt = family.Signed[8]
    UInt = family.Unsigned[8]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class fp_mux(Peak):
        def __call__(self, in0: Data, in1: Data, sel: Bit) -> Data:

            return Data(sel.ite(UInt(in0), UInt(in1)))

    return fp_mux
