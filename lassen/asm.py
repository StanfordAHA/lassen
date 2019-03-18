from dataclasses import dataclass
from .cond import Cond
from .mode import Mode
from .lut import Bit, LUT
from .isa import *

# https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec

#
# Format a configuration of the PE - sets all fields
#
def inst(alu, signed=0, lut=0, cond=Cond.Z,
    ra_mode=Mode.BYPASS, ra_const=0,
    rb_mode=Mode.BYPASS, rb_const=0,
    rd_mode=Mode.BYPASS, rd_const=0,
    re_mode=Mode.BYPASS, re_const=0,
    rf_mode=Mode.BYPASS, rf_const=0
    ):

    return Inst(alu, Signed(signed), LUT(lut), cond,
        RegA_Mode(ra_mode), RegA_Const(ra_const),
        RegB_Mode(rb_mode), RegB_Const(rb_const),
        RegD_Mode(rd_mode), RegD_Const(rd_const),
        RegE_Mode(re_mode), RegE_Const(re_const),
        RegF_Mode(rf_mode), RegF_Const(rf_const) )

# helper functions to format configurations

def add():
    return inst(ALUOP.Add)

def sub ():
    return inst(ALUOP.Sub)

def neg ():
    return inst(ALUOP.Sub)

def umult0 ():
    return inst(ALUOP.Mult0)

def umult1 ():
    return inst(ALUOP.Mult1)

def umult2 ():
    return inst(ALUOP.Mult2)

def smult0 ():
    return inst(ALUOP.Mult0, signed=1)

def smult1 ():
    return inst(ALUOP.Mult1, signed=1)

def smult2 ():
    return inst(ALUOP.Mult2, signed=1)

def fgetmant ():
    return inst(ALUOP.FGetMant)

def fp_add():
    return inst(ALUOP.FP_add)

def fp_mult():
    return inst(ALUOP.FP_mult)

def faddiexp ():
    return inst(ALUOP.FAddIExp)

def fsubexp ():
    return inst(ALUOP.FSubExp)

def fcnvexp2f ():
    return inst(ALUOP.FCnvExp2F)

def fgetfint ():
    return inst(ALUOP.FGetFInt)

def fgetffrac ():
    return inst(ALUOP.FGetFFrac)

def and_():
    return inst(ALUOP.And)

def or_():
    return inst(ALUOP.Or)

def xor():
    return inst(ALUOP.XOr)

def lsl():
    return inst(ALUOP.SHL)

def lsr():
    return inst(ALUOP.SHR)

def asr():
    return inst(ALUOP.SHR, signed=1)

def sel():
    return inst(ALUOP.Sel)

def abs():
    return inst(ALUOP.Abs, signed=1)

def umin():
    return inst(ALUOP.LTE_Min)

def umax():
    return inst(ALUOP.GTE_Max)

def smin():
    return inst(ALUOP.LTE_Min, signed=1)

def smax():
    return inst(ALUOP.GTE_Max, signed=1)

def eq():
    return inst(ALUOP.Sub, cond=Cond.Z)

def ne():
    return inst(ALUOP.Sub, cond=Cond.Z_n)

def ult():
    return inst(ALUOP.Sub, cond=Cond.ULT)

def ule():
    return inst(ALUOP.Sub, cond=Cond.ULE)

def ugt():
    return inst(ALUOP.Sub, cond=Cond.UGT)

def uge():
    return inst(ALUOP.Sub, cond=Cond.UGE)

def slt():
    return inst(ALUOP.Sub, cond=Cond.SLT)

def sle():
    return inst(ALUOP.Sub, cond=Cond.SLE)

def sgt():
    return inst(ALUOP.Sub, cond=Cond.SGT)

def sge():
    return inst(ALUOP.Sub, cond=Cond.SGE)

