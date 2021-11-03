
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def ult_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class ult(Peak):
        def __call__(self, in0 : Data, in1 : Data) -> Bit:
            
            return Bit(UInt(in1) < UInt(in0))
    
    return ult
    