from peak import Peak, family_closure, Const
from peak import family
from peak import name_outputs
from peak.family import AbstractFamily
from peak.family import MagmaFamily, SMTFamily
import magma
from hwtypes import SMTFPVector, FPVector, RoundingMode
from peak.float import float_lib_gen, RoundingMode

float_lib = float_lib_gen(8, 7)

DATAWIDTH = 16
def BFloat16_fc(family):
    if isinstance(family, MagmaFamily):
        BFloat16 =  magma.BFloat[8, 7, RoundingMode.RNE, False]
        BFloat16.reinterpret_from_bv = lambda bv: BFloat16(bv)
        BFloat16.reinterpret_as_bv = lambda f: magma.Bits[16](f)
        return BFloat16
    elif isinstance(family, SMTFamily):
        FPV = SMTFPVector
    else:
        FPV = FPVector
    BFloat16 = FPV[8, 7, RoundingMode_hw.RNE, False]
    return BFloat16

@family_closure
def fp_abs_max_fc(family: AbstractFamily):

    FPAdd = float_lib.const_rm(RoundingMode.RNE).Add_fc(family)
    Data = family.BitVector[16]


    @family.assemble(locals(), globals())
    class fp_abs_max(Peak):
        def __init__(self):
            self.Add: FPAdd = FPAdd()

        def __call__(self, in0 : Data, in1 : Data) -> Data:

            abs_mask = Data((2 ** (DATAWIDTH - 1)) - 1)
            abs_in0 = in0 & abs_mask
            abs_in1 = in1 & abs_mask

            abs_in1_neg = abs_in1 ^ (2 ** (DATAWIDTH - 1))
            res = Data(self.Add(abs_in0, abs_in1_neg))
            N = res[-1]

            if N:
                selected = abs_in1
            else:
                selected = abs_in0

            return selected

    return fp_abs_max