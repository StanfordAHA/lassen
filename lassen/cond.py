from peak.adt import Enum
import magma as m
from functools import lru_cache


@lru_cache()
def gen_cond_type(family):
    """
    Condition code field - selects which 1-bit result is retuned
    """
    class Cond(family.Enum):
        Z = 0    # EQ
        Z_n = 1  # NE
        C = 2    # UGE
        C_n = 3  # ULT
        N = 4    # <  0
        N_n = 5  # >= 0
        V = 6    # Overflow
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
    return Cond


def gen_cond(family):
    #
    # Implement condition code logic
    #
    # Inputs are the condition code field, the alu result, the lut result,
    # and the flags Z, N, C, V
    #
    Cond = gen_cond_type(family)
    Bit = family.Bit

    def cond(code: Cond, alu: Bit, lut: Bit, Z: Bit, N: Bit, C: Bit, V: Bit) \
            -> Bit:
        if code == Cond.Z:
            return Z
        elif code == Cond.Z_n:
            return not Z
        elif code == Cond.C or code == Cond.UGE:
            return C
        elif code == Cond.C_n or code == Cond.ULT:
            return not C
        elif code == Cond.N:
            return N
        elif code == Cond.N_n:
            return not N
        elif code == Cond.V:
            return V
        elif code == Cond.V_n:
            return not V
        elif code == Cond.UGT:
            return C and not Z
        elif code == Cond.ULE:
            return not C or Z
        elif code == Cond.SGE:
            return N == V
        elif code == Cond.SLT:
            return N != V
        elif code == Cond.SGT:
            return not Z and (N == V)
        elif code == Cond.SLE:
            return Z or (N != V)
        elif code == Cond.ALU:
            return alu
        elif code == Cond.LUT:
            return lut
    if family.Bit is m.Bit:
        cond = m.circuit.combinational(cond)
    return cond
