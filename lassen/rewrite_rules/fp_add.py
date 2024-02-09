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
def fp_add_fc(family: AbstractFamily):

    FPAdd = float_lib.const_rm(RoundingMode.RNE).Add_fc(family)
    Data = family.BitVector[16]

    @family.assemble(locals(), globals())
    class fp_add(Peak):
        def __init__(self):
            self.Add: FPAdd = FPAdd()

        def __call__(self, in0 : Data, in1 : Data) -> Data:
            return Data(self.Add(in0, in1))
    
    return fp_add