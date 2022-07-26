
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def ucrop_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class ucrop(Peak):
        def __call__(self, in0 : Data, in1 : Data, in2 : Data) -> Data:
            min_in0_in1 = (UInt(in0) <= UInt(in1)).ite(UInt(in0), UInt(in1))
            return Data((UInt(min_in0_in1) >= UInt(in2)).ite(UInt(min_in0_in1), UInt(in2)))
    
    return ucrop