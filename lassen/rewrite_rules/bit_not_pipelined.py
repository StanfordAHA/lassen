
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def bit_not_pipelined_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class bit_not_pipelined(Peak):
        def __call__(self, in0 : Const(Bit)) -> Bit:
            
            return Bit(~in0)
    
    return bit_not_pipelined
    