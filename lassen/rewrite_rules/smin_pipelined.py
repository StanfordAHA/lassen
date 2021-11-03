
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def smin_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class smin(Peak):
        def __call__(self, in0 : Data, in1 : Data) -> Data:
            
            return Data((SInt(in1) <= SInt(in0)).ite(SInt(in1), SInt(in0)))
    
    return smin
    