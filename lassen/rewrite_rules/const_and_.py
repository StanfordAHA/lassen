
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def const_and__fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class const_and_(Peak):
        def __call__(self, in1 : Data, in0 : Const(Data)) -> Data:
            
            return Data(UInt(in0) & UInt(in1))
    
    return const_and_
    