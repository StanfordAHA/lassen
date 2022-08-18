from hwtypes.adt import Enum
from peak import Peak, family_closure, Const, name_outputs
from hwtypes import Bit, BitVector
from peak.float import float_lib_gen, RoundingMode

Data = BitVector[16]


class FPU_t(Enum):
    FP_add = 0
    FP_sub = 1
    FP_cmp = 2
    FP_mul = 3


float_lib = float_lib_gen(8, 7)


@family_closure
def FPU_fc(family):

    FPAdd = float_lib.const_rm(RoundingMode.RNE).Add_fc(family)
    FPMul = float_lib.const_rm(RoundingMode.RNE).Mul_fc(family)

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

    @family.assemble(locals(), globals(), set_port_names=True)
    class FPU(Peak):
        def __init__(self):
            self.Add: FPAdd = FPAdd()
            self.Mul: FPMul = FPMul()

        @name_outputs(res=Data, N=Bit, Z=Bit)
        def __call__(self, fpu_op: Const(FPU_t), a: Data, b: Data) -> (Data, Bit, Bit):

            a_inf = fp_is_inf(a)
            b_inf = fp_is_inf(b)
            a_neg = fp_is_neg(a)
            b_neg = fp_is_neg(b)

            neg_b = (fpu_op == FPU_t.FP_sub) | (fpu_op == FPU_t.FP_cmp)
            if neg_b:
                b = b ^ (2 ** (16 - 1))
            Add_val = self.Add(a, b)
            Mul_val = self.Mul(a, b)
            if (
                (fpu_op == FPU_t.FP_add)
                | (fpu_op == FPU_t.FP_sub)
                | (fpu_op == FPU_t.FP_cmp)
            ):
                res = Add_val
            else:
                res = Mul_val

            Z = fp_is_zero(res)
            # Nicely handles infinities for comparisons
            if fpu_op == FPU_t.FP_cmp:
                if (a_inf & b_inf) & (a_neg == b_neg):
                    Z = family.Bit(1)

            N = family.Bit(res[-1])
            return res, N, Z

    return FPU
