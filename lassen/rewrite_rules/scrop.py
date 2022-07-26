
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def scrop_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class scrop(Peak):
        def __call__(self, in0 : Data, in1 : Data, in2 : Data) -> Data:
            min_in0_in1 = (SInt(in0) <= SInt(in1)).ite(SInt(in0), SInt(in1))
            return Data((SInt(min_in0_in1) >= SInt(in2)).ite(SInt(min_in0_in1), SInt(in2)))
    
    return scrop
    