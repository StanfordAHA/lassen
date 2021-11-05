
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def sge_const_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class sge_const(Peak):
        def __call__(self, in0 : Data, in1 : Const(Data)) -> Bit:
            
            return Bit(SInt(in1) >= SInt(in0))
    
    return sge_const
    