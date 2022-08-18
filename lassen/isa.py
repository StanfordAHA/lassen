from .cond import Cond_t
from .mode import Mode_t
from .lut import LUT_t_fc
from .alu import ALU_t, Signed_t
from .float.fpu import FPU_t
from .float.float_custom import FPCustom_t
from .common import DATAWIDTH
from peak import Const, family_closure
from hwtypes.adt import Product, TaggedUnion


class Op_t(TaggedUnion):
    alu = ALU_t
    fpu = FPU_t
    fp_custom = FPCustom_t


@family_closure
def Inst_fc(family):
    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit

    LUT_t, _ = LUT_t_fc(family)

    class Inst(Product):
        op = Op_t
        signed = Signed_t  # unsigned or signed
        lut = LUT_t  # LUT operation as a 3-bit LUT
        cond = Cond_t  # Condition code (see cond.py)
        rega = Mode_t  # RegA mode (see mode.py)
        data0 = Data  # RegA constant (16-bits)
        regb = Mode_t  # RegB mode
        data1 = Data  # RegB constant (16-bits)
        regc = Mode_t  # RegC mode
        data2 = Data  # RegC constant (16-bits)
        regd = Mode_t  # RegD mode
        bit0 = Bit  # RegD constant (1-bit)
        rege = Mode_t  # RegE mode
        bit1 = Bit  # RegE constant (1-bit)
        regf = Mode_t  # RegF mode
        bit2 = Bit  # RegF constant (1-bit)

    return Inst
