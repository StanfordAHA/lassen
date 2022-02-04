
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def const_abs_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class const_abs(Peak):
        def __call__(self, in0 : Const(Data)) -> Data:
            
            return Data((SInt(in0) >= SInt(0)).ite(SInt(in0), SInt(in0)*SInt(-1)))
    
    return const_abs
    