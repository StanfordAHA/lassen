from hwtypes.adt import Product
from .cond import Cond_t_fc
from .mode import Mode_t_fc
from .lut import LUT_t_fc
from .alu import ALU_t_fc
from .common import DATAWIDTH

"""
https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
"""
def Inst_fc(family):
    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit

    LUT_t, _ = LUT_t_fc(family)
    Cond_t = Cond_t_fc(family)
    Mode_t = Mode_t_fc(family)
    ALU_t, Signed_t = ALU_t_fc(family)
    class Inst(Product):
        alu= ALU_t          # ALU operation
        signed= Signed_t     # unsigned or signed
        lut= LUT_t          # LUT operation as a 3-bit LUT
        cond= Cond_t        # Condition code (see cond.py)
        rega= Mode_t        # RegA mode (see mode.py)
        data0= Data         # RegA constant (16-bits)
        regb= Mode_t        # RegB mode
        data1= Data         # RegB constant (16-bits)
        regd= Mode_t        # RegD mode
        bit0= Bit           # RegD constant (1-bit)
        rege= Mode_t        # RegE mode
        bit1= Bit           # RegE constant (1-bit)
        regf= Mode_t        # RegF mode
        bit2= Bit           # RegF constant (1-bit)
    return Inst
