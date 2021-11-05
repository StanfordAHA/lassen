
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def const_ule_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class const_ule(Peak):
        def __call__(self, in0 : Const(Data), in1 : Data) -> Bit:
            
            return Bit(UInt(in1) <= UInt(in0))
    
    return const_ule
    