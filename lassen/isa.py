from hwtypes import BitVector, Bit
from hwtypes.adt import Enum, Product
from .cond import gen_cond_type
from .mode import gen_mode_type
from .lut import gen_lut_type
import magma as m
from functools import lru_cache


@lru_cache()
def gen_alu_type(family):
    class ALU(family.Enum):
        Add = 0
        Sub = 1
        Adc = 2
        Sbc = 6
        Abs = 3
        GTE_Max = 4
        LTE_Min = 5
        Sel = 8
        Mult0 = 0xb
        Mult1 = 0xc
        Mult2 = 0xd
        SHR = 0xf
        SHL = 0x11
        Or = 0x12
        And = 0x13
        XOr = 0x14
        FP_add = 0x16
        FP_sub = 0x17
        FP_cmp = 0x18
        FP_mult = 0x19
        FGetMant = 0x92
        FAddIExp = 0x93
        FSubExp = 0x94
        FCnvExp2F = 0x95
        FGetFInt = 0x96
        FGetFFrac = 0x97
        FCnvInt2F = 0x98
    return ALU

@lru_cache()
def gen_signed_type(family):
    """
    Whether the operation is unsigned (0) or signed (1)
    """
    class Signed(family.Enum):
        unsigned = 0
        signed = 1
    return Signed


# Current PE has 16-bit data path
DATAWIDTH = 16

@lru_cache()
def gen_inst_type(family):
    """
    https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
    """
    ALU = gen_alu_type(family)
    Signed = gen_signed_type(family)

    Data = family.BitVector[DATAWIDTH]
    # Constant values for registers
    RegA_Const = family.BitVector[DATAWIDTH]
    RegB_Const = family.BitVector[DATAWIDTH]
    RegD_Const = family.Bit
    RegE_Const = family.Bit
    RegF_Const = family.Bit

    Mode = gen_mode_type(family)
    LUT = gen_lut_type(family)
    Cond = gen_cond_type(family)

    # Modes for registers
    RegA_Mode = Mode
    RegB_Mode = Mode
    RegD_Mode = Mode
    RegE_Mode = Mode
    RegF_Mode = Mode

    class Inst(family.Product):
        """
        Each configuration is given by the following fields
        """
        alu= ALU           # ALU operation
        signed_= Signed    # unsigned or signed
        lut= LUT           # LUT operation as a 3-bit LUT
        cond= Cond         # Condition code (see cond.py)
        rega= RegA_Mode    # RegA mode (see mode.py)
        data0= RegA_Const  # RegA constant (16-bits)
        regb= RegB_Mode    # RegB mode
        data1= RegB_Const  # RegB constant (16-bits)
        regd= RegD_Mode    # RegD mode
        bit0= RegD_Const   # RegD constant (1-bit)
        rege= RegE_Mode    # RegE mode
        bit1= RegE_Const   # RegE constant (1-bit)
        regf= RegF_Mode    # RegF mode
        bit2= RegF_Const   # RegF constant (1-bit)
    return Inst

