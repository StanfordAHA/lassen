from hwtypes import BitVector, Bit
from hwtypes.adt import Enum, Product
from .cond import Cond_t
from .mode import Mode_t
from .lut import LUT_t
from .alu import ALU_t, Signed_t
from .common import Data, DATAWIDTH

DataConst = Data
BitConst = Bit

"""
https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
"""
class Inst(Product):
    """
    Each configuration is given by the following fields
    """
    alu= ALU_t          # ALU operation
    signed= Signed_t     # unsigned or signed
    lut= LUT_t          # LUT operation as a 3-bit LUT
    cond= Cond_t        # Condition code (see cond.py)
    rega= Mode_t        # RegA mode (see mode.py)
    data0= DataConst         # RegA constant (16-bits)
    regb= Mode_t        # RegB mode
    data1= DataConst         # RegB constant (16-bits)
    regd= Mode_t        # RegD mode
    bit0= BitConst           # RegD constant (1-bit)
    rege= Mode_t        # RegE mode
    bit1= BitConst           # RegE constant (1-bit)
    regf= Mode_t        # RegF mode
    bit2= BitConst           # RegF constant (1-bit)
