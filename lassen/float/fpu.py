from hwtypes.adt import Enum
from peak import Peak, family_closure, Const, name_outputs
from hwtypes import Bit, BitVector
from ..common import DATAWIDTH, BFloat16_fc

Data = BitVector[16]
class FPU_t(Enum):
    FP_add = 0
    FP_sub = 1
    FP_cmp = 2
    FP_mul = 3


@family_closure
def FPU_fc(family):

    BFloat16 = BFloat16_fc(family)
    FPExpBV = family.BitVector[8]
    FPFracBV = family.BitVector[7]

    def bv2float(bv):
        return BFloat16.reinterpret_from_bv(bv)

    def float2bv(bvf):
        return BFloat16.reinterpret_as_bv(bvf)

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
        @name_outputs(res=Data, N=Bit, Z=Bit)
        def __call__(self, fpu_op: Const(FPU_t), a: Data, b: Data) -> (Data, Bit, Bit):

            a_inf = fp_is_inf(a)
            b_inf = fp_is_inf(b)
            a_neg = fp_is_neg(a)
            b_neg = fp_is_neg(b)

            if (fpu_op == FPU_t.FP_add) | (fpu_op == FPU_t.FP_sub) | (fpu_op == FPU_t.FP_cmp):
                if (fpu_op == FPU_t.FP_sub) | (fpu_op == FPU_t.FP_cmp):
                    b = b ^ (2**(16-1))
                a_fpadd = bv2float(a)
                b_fpadd = bv2float(b)
                res = float2bv(a_fpadd + b_fpadd)
            else: #fpu_op == FPU_t.FP_mul:
                a_fpmul = bv2float(a)
                b_fpmul = bv2float(b)
                res = float2bv(a_fpmul * b_fpmul) 
            
            Z = fp_is_zero(res)
            # Nicely handles infinities for comparisons
            if (fpu_op == FPU_t.FP_cmp):
                if (a_inf & b_inf) & (a_neg == b_neg):
                    Z = family.Bit(1)

            N = family.Bit(res[-1])
            return res, N, Z
    return FPU
