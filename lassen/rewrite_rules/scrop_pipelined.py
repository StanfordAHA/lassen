
from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily

@family_closure
def scrop_pipelined_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class scrop_pipelined(Peak):
        def __call__(self, in0 : Data, in1 : Data, in2 : Data) -> Data:
            max_in1_in2 = (SInt(in1) >= SInt(in0)).ite(SInt(in1), SInt(in0))
            crop_in1_in2_in3 = (SInt(in2) <= max_in1_in2).ite(SInt(in2), max_in1_in2)
            return Data(crop_in1_in2_in3)
    
    return scrop_pipelined
    