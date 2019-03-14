from hwtypes import BitVector, Bit
from peak.adt import Enum, Product
from .cond import gen_cond_type
from .mode import gen_mode
from .lut import Bit, gen_lut_type
import magma as m

def gen_alu(mode="sim"):
    # ALU operations
    if mode == "sim":
        class ALU(Enum):
            Add = 0
            Sub = 1
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
            FP_add = 0x15
            FP_mult = 0x16
            FGetMant     = 0x92
            FAddIExp     = 0x93
            FSubExp      = 0x94
            FCnvExp2F    = 0x95
            FGetFInt     = 0x96
            FGetFFrac    = 0x97
    elif mode == "rtl":
        ALU = m.Enum(
            Add = 0,
            Sub = 1,
            Abs = 3,
            GTE_Max = 4,
            LTE_Min = 5,
            Sel = 8,
            Mult0 = 0xb,
            Mult1 = 0xc,
            Mult2 = 0xd,
            SHR = 0xf,
            SHL = 0x11,
            Or = 0x12,
            And = 0x13,
            XOr = 0x14,
            FP_add = 0x15,
            FP_mult = 0x16,
            FGetMant     = 0x92,
            FAddIExp     = 0x93,
            FSubExp      = 0x94,
            FCnvExp2F    = 0x95,
            FGetFInt     = 0x96,
            FGetFFrac    = 0x97,
        )
    return ALU

def gen_signed(mode="sim"):
    # Whether the operation is unsigned (0) or signed (1)
    if mode == "sim":
        class Signed(Enum):
            unsigned = 0
            signed = 1
    elif mode == "rtl":
        Signed = m.Enum(
            unsigned = 0,
            signed = 1
        )
    return Signed


# Current PE has 16-bit data path
DATAWIDTH = 16


def gen_inst(mode="sim"):
    ALU = gen_alu(mode)
    Signed = gen_signed(mode)


    # https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec


    if mode == "sim":
        family = BitVector.get_family()
    elif mode == "rtl":
        family = m.get_family()

    Data = family.BitVector[DATAWIDTH]
    # Constant values for registers
    RegA_Const = family.BitVector[DATAWIDTH]
    RegB_Const = family.BitVector[DATAWIDTH]
    RegD_Const = family.Bit
    RegE_Const = family.Bit
    RegF_Const = family.Bit

    Mode = gen_mode(mode)
    LUT = gen_lut_type(family)
    Cond = gen_cond_type(mode)

    # Modes for registers
    RegA_Mode = Mode
    RegB_Mode = Mode
    RegD_Mode = Mode
    RegE_Mode = Mode
    RegF_Mode = Mode
    if mode == "sim":
#
# Each configuration is given by the following fields
#
        class Inst(Product):
            alu:ALU          # ALU operation
            signed_:Signed    # unsigned or signed 
            lut:LUT          # LUT operation as a 3-bit LUT
            cond:Cond        # Condition code (see cond.py)
            rega:RegA_Mode   # RegA mode (see mode.py)
            data0:RegA_Const # RegA constant (16-bits)
            regb:RegB_Mode   # RegB mode
            data1:RegB_Const # RegB constant (16-bits)
            regd:RegD_Mode   # RegD mode
            bit0:RegD_Const  # RegD constant (1-bit)
            rege:RegE_Mode   # RegE mode
            bit1:RegE_Const  # RegE constant (1-bit)
            regf:RegF_Mode   # RegF mode
            bit2:RegF_Const  # RegF constant (1-bit)
    elif mode == "rtl":
        Inst = m.Tuple(
            alu=ALU,  # ALU operation
            signed_=Signed,  # unsigned or signed
            lut=LUT,  # LUT operation as a 3-bit LUT
            cond=Cond,  # Condition code (see cond.py)
            rega=RegA_Mode,  # RegA mode (see mode.py)
            data0=RegA_Const,  # RegA constant (16-bits)
            regb=RegB_Mode,  # RegB mode
            data1=RegB_Const,  # RegB constant (16-bits)
            regd=RegD_Mode,  # RegD mode
            bit0=RegD_Const,  # RegD constant (1-bit)
            rege=RegE_Mode,  # RegE mode
            bit1=RegE_Const,  # RegE constant (1-bit)
            regf=RegF_Mode,  # RegF mode
            bit2=RegF_Const    # RegF constant (1-bit)
        )
    return Inst

