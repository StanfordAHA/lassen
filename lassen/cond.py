from peak import Peak, family_closure, name_outputs
from hwtypes.adt import Enum

"""
Condition code field - selects which 1-bit result is retuned
"""


class Cond_t(Enum):
    Z = 0  # EQ
    Z_n = 1  # NE
    C = 2  # UGE
    C_n = 3  # ULT
    # Prefix _N because it clobbers magma's `.N` field used in the array
    # types
    _N = 4  # <  0
    _N_n = 5  # >= 0
    V = 6  # Overflow
    V_n = 7  # No overflow
    EQ = 0
    NE = 1
    UGE = 2
    ULT = 3
    UGT = 8
    ULE = 9
    SGE = 10
    SLT = 11
    SGT = 12
    SLE = 13
    LUT = 14
    ALU = 15
    FP_EQ = 0
    FP_NE = 1
    FP_GE = 16
    FP_GT = 17
    FP_LE = 18
    FP_LT = 19


#
# Implement condition code logic
#
# Inputs are the condition code field, the alu result, the lut result,
# and the flags Z, N, C, V
#
# Every condition is computed at once and one AND-OR picks the selected one.
# A 20-way if/elif here synthesized into a serial chain of 19 2:1 muxes on the
# PE's predicate path (operand -> ALU flags -> Cond -> res_p, the PE's worst
# path at every data width), which a hierarchical (unflattened) synthesis
# cannot rebalance. Now a flag passes 1-2 gates, an AND with its select and a
# 5-level OR tree. The selects depend only on the (configuration) code.
# Same function as the chain, including the encodings no Cond_t names: like
# the chain's final `else`, they give FP_LT.
#
@family_closure
def Cond_fc(family):
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class Cond(Peak):
        @name_outputs(cond=Bit)
        def __call__(
            self, code: Cond_t, alu: Bit, lut: Bit, Z: Bit, N: Bit, C: Bit, V: Bit
        ) -> Bit:
            s_z = Bit(code == Cond_t.Z)
            s_zn = Bit(code == Cond_t.Z_n)
            s_c = Bit(code == Cond_t.C)
            s_cn = Bit(code == Cond_t.C_n)
            s_n = Bit(code == Cond_t._N)
            s_nn = Bit(code == Cond_t._N_n)
            s_v = Bit(code == Cond_t.V)
            s_vn = Bit(code == Cond_t.V_n)
            s_ugt = Bit(code == Cond_t.UGT)
            s_ule = Bit(code == Cond_t.ULE)
            s_sge = Bit(code == Cond_t.SGE)
            s_slt = Bit(code == Cond_t.SLT)
            s_sgt = Bit(code == Cond_t.SGT)
            s_sle = Bit(code == Cond_t.SLE)
            s_alu = Bit(code == Cond_t.ALU)
            s_lut = Bit(code == Cond_t.LUT)
            s_fge = Bit(code == Cond_t.FP_GE)
            s_fgt = Bit(code == Cond_t.FP_GT)
            s_fle = Bit(code == Cond_t.FP_LE)
            # FP_LT and every unnamed encoding (the chain's `else`)
            m0 = (s_z | s_zn) | (s_c | s_cn)
            m1 = (s_n | s_nn) | (s_v | s_vn)
            m2 = (s_ugt | s_ule) | (s_sge | s_slt)
            m3 = (s_sgt | s_sle) | (s_alu | s_lut)
            m4 = (s_fge | s_fgt) | s_fle
            s_flt = ~(((m0 | m1) | (m2 | m3)) | m4)

            # each condition, then AND with its select
            nv = N == V
            c_ugt = C & ~Z
            c_ule = ~C | Z
            c_sgt = ~Z & nv
            c_sle = Z | ~nv
            c_fge = ~N | Z
            c_fgt = ~N & ~Z
            c_fle = N | Z
            c_flt = N & ~Z
            t0 = ((s_z & Z) | (s_zn & ~Z)) | ((s_c & C) | (s_cn & ~C))
            t1 = ((s_n & N) | (s_nn & ~N)) | ((s_v & V) | (s_vn & ~V))
            t2 = ((s_ugt & c_ugt) | (s_ule & c_ule)) | \
                ((s_sge & nv) | (s_slt & ~nv))
            t3 = ((s_sgt & c_sgt) | (s_sle & c_sle)) | \
                ((s_alu & alu) | (s_lut & lut))
            t4 = ((s_fge & c_fge) | (s_fgt & c_fgt)) | \
                ((s_fle & c_fle) | (s_flt & c_flt))
            return ((t0 | t1) | (t2 | t3)) | t4

    return Cond
