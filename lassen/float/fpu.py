from hwtypes.adt import Enum
from peak import Peak, family_closure, Const, name_outputs
from hwtypes import Bit, BitVector
from peak.float import float_lib_gen, RoundingMode
from peak.family import PyFamily
from lassen.utils import bfbin2float, float2bfbin

Data = BitVector[16]


class FPU_t(Enum):
    FP_add = 0
    FP_sub = 1
    FP_cmp = 2
    FP_mul = 3
    FP_max = 4
    FP_abs_max = 5

float_lib = float_lib_gen(8, 7)

@family_closure
def FPU_fc(family):

    FPAdd = float_lib.const_rm(RoundingMode.RNE).Add_fc(family)
    FPMul = float_lib.const_rm(RoundingMode.RNE).Mul_fc(family)

    class FPU_Mul_10_Bit_Rounding(Peak):
        def __init__(self):
            self.Mul: FPMul = FPMul()

        @name_outputs(res=Data)
        def __call__(self, a: Data, b: Data) -> Data:
            if family == PyFamily():

                a_float = bfbin2float("{:016b}".format(int(a)))
                b_float = bfbin2float("{:016b}".format(int(b)))

                res_float = float(a_float) * float(b_float)
                bin_float = float2bfbin(res_float)


                return Data(int(bin_float, 2))
            else:
                return self.Mul(a, b)

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
            self.Mul: FPU_Mul_10_Bit_Rounding = FPU_Mul_10_Bit_Rounding()

        @name_outputs(res=Data, N=Bit, Z=Bit)
        def __call__(self, fpu_op: Const(FPU_t), a: Data, b: Data) -> (Data, Bit, Bit):

            a_inf = fp_is_inf(a)
            b_inf = fp_is_inf(b)
            a_neg = fp_is_neg(a)
            b_neg = fp_is_neg(b)

            old_b = b
            neg_b = (fpu_op == FPU_t.FP_sub) | (fpu_op == FPU_t.FP_cmp) | (fpu_op == FPU_t.FP_max)
            if neg_b:
                b = b ^ (2 ** (16 - 1))

            abs_mask  = Data((1 << 15) - 1)
            abs_a     = a & abs_mask
            abs_b     = b & abs_mask
            abs_b_neg = abs_b ^ (1 << 15)

            use_abs = family.Bit(fpu_op == FPU_t.FP_abs_max)
            add_in0 = use_abs.ite(abs_a, a)
            add_in1 = use_abs.ite(abs_b_neg, b)
            Add_val = self.Add(add_in0, add_in1)
            Mul_val = self.Mul(a, b)
            if (
                (fpu_op == FPU_t.FP_add)
                | (fpu_op == FPU_t.FP_sub)
                | (fpu_op == FPU_t.FP_cmp)
            ):
                res = Add_val
            elif (fpu_op == FPU_t.FP_max):
                # if add_val negative then b is bigger
                if family.Bit(Add_val[-1]):
                    res = old_b
                else:
                    res = a
            elif (fpu_op == FPU_t.FP_abs_max):
                # If abs_diff is negative, then abs_b is bigger in magnitude
                if family.Bit(Add_val[-1]):
                    res = abs_b
                else:
                    res = abs_a
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
