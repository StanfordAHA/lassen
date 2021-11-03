
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def mux_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class mux(Peak):
        def __call__(self, in1 : Data, in0 : Data, sel : Bit) -> Data:
            
            return Data(sel.ite(UInt(in1),UInt(in0)))
    
    return mux
    