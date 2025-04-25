from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode


DATAWIDTH = 16

@family_closure
def get_shared_exp_fc(family: AbstractFamily):
    Data   = family.BitVector[16]
    UInt8  = family.Unsigned[8]
    BitVector = family.BitVector

    @family.assemble(locals(), globals())
    class get_shared_exp(Peak):
        def __call__(self, in0: Data) -> Data:
            exp8 = UInt8(in0[7:15])

            if exp8 == UInt8(0):
                # Note: set to 127 to set scale value to 1.0 (2^(127-127))
                shared8 = UInt8(127)
            else:
                # Note: in rare case where exp8 is small, we will let it overflow and wrap as what voyager does
                shared8 = exp8 - UInt8(6)

            # zero-extend back to 16 bits
            return Data(shared8.zext(8))

    return get_shared_exp

