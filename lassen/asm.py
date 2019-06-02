from dataclasses import dataclass
from .cond import gen_cond_type
from .mode import gen_mode_type
from .lut import gen_lut_type
from .isa import *
from .sim import gen_pe_type_family
from hwtypes import BitVector

sim_family = gen_pe_type_family(BitVector.get_family())
Mode = gen_mode_type(sim_family)
ALU = gen_alu_type(sim_family)
Inst = gen_inst_type(sim_family)
LUT = gen_lut_type(sim_family)
Signed = gen_signed_type(sim_family)
DataConst = sim_family.BitVector[DATAWIDTH]
BitConst = sim_family.Bit
Cond = gen_cond_type(sim_family)

#Lut Constants
B0 = BitVector[8]([0,1,0,1,0,1,0,1])
B1 = BitVector[8]([0,0,1,1,0,0,1,1])
B2 = BitVector[8]([0,0,0,0,1,1,1,1])


def inst(alu, signed=Signed.unsigned, lut=0, cond=Cond.Z,
         ra_mode=Mode.BYPASS, ra_const=0,
         rb_mode=Mode.BYPASS, rb_const=0,
         rd_mode=Mode.BYPASS, rd_const=0,
         re_mode=Mode.BYPASS, re_const=0,
         rf_mode=Mode.BYPASS, rf_const=0):
    """
    https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
    Format a configuration of the PE - sets all fields
    """
    return Inst(alu, Signed(signed), LUT(lut), cond,
                Mode(ra_mode), DataConst(ra_const), Mode(rb_mode),
                DataConst(rb_const), Mode(rd_mode), BitConst(rd_const),
                Mode(re_mode), BitConst(re_const), Mode(rf_mode),
                BitConst(rf_const))

# helper functions to format configurations

def add(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS, ra_const=0, rb_const=0):
    return inst(ALU.Add, ra_mode=ra_mode, rb_mode=rb_mode, ra_const=ra_const,
                rb_const=rb_const)

def sub ():
    return inst(ALU.Sub)

def neg ():
    return inst(ALU.Sub)

def umult0 ():
    return inst(ALU.Mult0)

def umult1 ():
    return inst(ALU.Mult1)

def umult2 ():
    return inst(ALU.Mult2)

def smult0 ():
    return inst(ALU.Mult0, signed=Signed.signed)

def smult1 ():
    return inst(ALU.Mult1, signed=Signed.signed)

def smult2 ():
    return inst(ALU.Mult2, signed=Signed.signed)

def fgetmant ():
    return inst(ALU.FGetMant)

def fp_add(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FP_add, ra_mode=ra_mode, rb_mode=rb_mode)

def fp_mult(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FP_mult, ra_mode=ra_mode, rb_mode=rb_mode)

def fp_sub(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FP_sub, ra_mode=ra_mode, rb_mode=rb_mode)

def faddiexp (ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FAddIExp, ra_mode=ra_mode, rb_mode=rb_mode)

def fsubexp (ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FSubExp, ra_mode=ra_mode, rb_mode=rb_mode)

def fcnvexp2f (ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FCnvExp2F, ra_mode=ra_mode, rb_mode=rb_mode)

def fgetfint (ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FGetFInt, ra_mode=ra_mode, rb_mode=rb_mode)

def fgetffrac (ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.FGetFFrac, ra_mode=ra_mode, rb_mode=rb_mode)

def and_(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.And, ra_mode=ra_mode, rb_mode=rb_mode)

def or_(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.Or, ra_mode=ra_mode, rb_mode=rb_mode)

def xor(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.XOr, ra_mode=ra_mode, rb_mode=rb_mode)

def lsl():
    return inst(ALU.SHL)

def lsr():
    return inst(ALU.SHR)

def asr(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.SHR, ra_mode=ra_mode, rb_mode=rb_mode,
                signed=Signed.signed)

def sel():
    return inst(ALU.Sel)

def abs():
    return inst(ALU.Abs, signed=Signed.signed)

def umin():
    return inst(ALU.LTE_Min, cond=Cond.ALU)

def umax():
    return inst(ALU.GTE_Max, cond=Cond.ALU)

def smin(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.LTE_Min, signed=Signed.signed, cond=Cond.ALU,
                ra_mode=ra_mode, rb_mode=rb_mode)

def smax(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.GTE_Max, signed=Signed.signed, cond=Cond.ALU,
                ra_mode=ra_mode, rb_mode=rb_mode)

def eq():
    return inst(ALU.Sub, cond=Cond.Z)

def ne():
    return inst(ALU.Sub, cond=Cond.Z_n)

def ult():
    return inst(ALU.Sub, cond=Cond.ULT)

def ule():
    return inst(ALU.Sub, cond=Cond.ULE)

def ugt():
    return inst(ALU.Sub, cond=Cond.UGT)

def uge():
    return inst(ALU.Sub, cond=Cond.UGE)

def slt():
    return inst(ALU.Sub, cond=Cond.SLT)

def sle():
    return inst(ALU.Sub, cond=Cond.SLE)

def sgt():
    return inst(ALU.Sub, cond=Cond.SGT)

def sge():
    return inst(ALU.Sub, cond=Cond.SGE)

# implements a constant using a register and add by zero
def const(val):
    return inst(ALU.Add,
                ra_mode=Mode.CONST, ra_const=val,
                rb_mode=Mode.CONST, rb_const=0)

def lut(val):
    return inst(ALU.Add,lut=val,cond=Cond.LUT)

#Using bit1 and bit2 since bit0 can be used in the ALU
def lut_and():
    return lut(B1&B2)

def lut_or():
    return lut(B1|B2)

def lut_xor():
    return lut(B1^B2)

def lut_not():
    return lut(~B1)

def lut_mux():
    return lut((B2&B1)|((~B2)&B0))

