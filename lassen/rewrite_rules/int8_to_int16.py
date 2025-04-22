from peak import Peak, family_closure
from peak.family import AbstractFamily


@family_closure
def int8_to_int16_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    SInt = family.Signed
    SInt8 = family.Signed[8]
    SInt16 = family.Signed[16]
    UInt8 = family.Unsigned[8]

    @family.assemble(locals(), globals())
    class int8_to_int16(Peak):
        def __call__(self, in0: Data) -> Data:

            int8_val = in0[0:8]
            signed_val = SInt8(int8_val)
            res = Data(signed_val.sext(8))

            return res

    return int8_to_int16
