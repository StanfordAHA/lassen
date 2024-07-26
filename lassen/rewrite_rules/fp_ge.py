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
def fp_ge_fc(family: AbstractFamily):

    FPAdd = float_lib.const_rm(RoundingMode.RNE).Add_fc(family)
    Data = family.BitVector[16]
    Bit = family.Bit

    def fp_get_exp(val: Data):
        return val[7:15]

    def fp_get_frac(val: Data):
        return val[:7]

    def fp_is_zero(val: Data):
        return (fp_get_exp(val) == 0) & (fp_get_frac(val) == 0)

    def fp_is_inf(val: Data):
        return (fp_get_exp(val) == -1) & (fp_get_frac(val) == 0)

    def fp_is_neg(val: Data):
        return family.Bit(val[-1])

    @family.assemble(locals(), globals())
    class fp_ge(Peak):
        def __init__(self):
            self.Add: FPAdd = FPAdd()

        def __call__(self, in0 : Data, in1 : Data) -> Bit:
            a_inf = fp_is_inf(in0)
            b_inf = fp_is_inf(in1)
            a_neg = fp_is_neg(in0)
            b_neg = fp_is_neg(in1)

            in1 = in1 ^ (2 ** (16 - 1))
            res = Data(self.Add(in0, in1))

            Z = fp_is_zero(res)
            if (a_inf & b_inf) & (a_neg == b_neg):
                Z = family.Bit(1)

            N = res[-1]

            return ~N | Z
    
    return fp_ge