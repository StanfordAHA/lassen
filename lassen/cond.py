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
@family_closure
def Cond_fc(family):
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class Cond(Peak):
        @name_outputs(cond=Bit)
        def __call__(
            self, code: Cond_t, alu: Bit, lut: Bit, Z: Bit, N: Bit, C: Bit, V: Bit
        ) -> Bit:
            if code == Cond_t.Z:
                return Z
            elif code == Cond_t.Z_n:
                return ~Z
            elif (code == Cond_t.C) | (code == Cond_t.UGE):
                return C
            elif (code == Cond_t.C_n) | (code == Cond_t.ULT):
                return ~C
            elif code == Cond_t._N:
                return N
            elif code == Cond_t._N_n:
                return ~N
            elif code == Cond_t.V:
                return V
            elif code == Cond_t.V_n:
                return ~V
            elif code == Cond_t.UGT:
                return C & (~Z)
            elif code == Cond_t.ULE:
                return (~C) | Z
            elif code == Cond_t.SGE:
                return N == V
            elif code == Cond_t.SLT:
                return N != V
            elif code == Cond_t.SGT:
                return (~Z) & (N == V)
            elif code == Cond_t.SLE:
                return Z | (N != V)
            elif code == Cond_t.ALU:
                return alu
            elif code == Cond_t.LUT:
                return lut
            elif code == Cond_t.FP_GE:
                return ~N | Z
            elif code == Cond_t.FP_GT:
                return ~N & ~Z
            elif code == Cond_t.FP_LE:
                return N | Z
            else:  # code == Cond_t.FP_LT:
                return N & ~Z

    return Cond
