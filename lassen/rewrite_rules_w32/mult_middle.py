from peak import Peak, family_closure, Const
from peak import family, name_outputs
from peak.family import AbstractFamily


@family_closure
def mult_middle_fc(family: AbstractFamily):
    Data = family.BitVector[32]
    Data32 = family.Signed[64]
    SInt = family.Signed[32]
    UInt = family.Unsigned[32]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class mult_middle(Peak):
        @name_outputs(out=Data)
        def __call__(self, in1: Data, in0: Data) -> Data:
            mul = Data32(SInt(in0).sext(32)) * Data32(SInt(in1).sext(32))
            return Data(mul[16:48])

    return mult_middle
