from peak import Peak, family_closure, Const
from peak import family, name_outputs
from peak.family import AbstractFamily

@family_closure
def mult_middle_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Signed[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit
    @family.assemble(locals(), globals())
    class mult_middle(Peak):
        @name_outputs(out=Data)
        def __call__(self, in1 : Data, in0 : Data) -> Data:
                mul = Data32(in0) * Data32(in1)
                res = mul >> 8
                return Data(res[0:16])
    return mult_middle
    