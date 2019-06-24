from dataclasses import dataclass
from .cond import gen_cond_type
from .mode import gen_mode_type
from .lut import gen_lut_type
from .isa import *
from .sim import gen_pe_type_family
from hwtypes import BitVector, Bit

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

def add(**kwargs):
    return inst(ALU.Add, **kwargs)

def sub(**kwargs):
    return inst(ALU.Sub, **kwargs)

def adc(**kwargs):
    return inst(ALU.Adc, **kwargs)

def sbc(**kwargs):
    return inst(ALU.Sbc, **kwargs)

def neg(**kwargs):
    return inst(ALU.Sub, **kwargs)

def umult0(**kwargs):
    return inst(ALU.Mult0, **kwargs)

def umult1(**kwargs):
    return inst(ALU.Mult1, **kwargs)

def umult2(**kwargs):
    return inst(ALU.Mult2, **kwargs)

def smult0(**kwargs):
    return inst(ALU.Mult0, signed=Signed.signed, **kwargs)

def smult1(**kwargs):
    return inst(ALU.Mult1, signed=Signed.signed, **kwargs)

def smult2(**kwargs):
    return inst(ALU.Mult2, signed=Signed.signed, **kwargs)

def fgetmant(**kwargs):
    return inst(ALU.FGetMant, **kwargs)

def fp_add(**kwargs):
    return inst(ALU.FP_add, **kwargs)

def fp_sub(**kwargs):
    return inst(ALU.FP_sub, **kwargs)

def fp_mul(**kwargs):
    return inst(ALU.FP_mult, **kwargs)

def fp_cmp(cond, **kwargs):
    return inst(ALU.FP_cmp, cond=cond, **kwargs)

def fp_gt(**kwargs):
    return fp_cmp(Cond.FP_GT, **kwargs)

def fp_ge(**kwargs):
    return fp_cmp(Cond.FP_GE, **kwargs)

def fp_lt(**kwargs):
    return fp_cmp(Cond.FP_LT, **kwargs)

def fp_le(**kwargs):
    return fp_cmp(Cond.FP_LE, **kwargs)

def fp_eq(**kwargs):
    return fp_cmp(Cond.FP_EQ, **kwargs)

def fp_neq(**kwargs):
    return fp_cmp(Cond.FP_NE, **kwargs)


def faddiexp(**kwargs):
    return inst(ALU.FAddIExp, **kwargs)

def fsubexp(**kwargs):
    return inst(ALU.FSubExp, **kwargs)

def fcnvexp2f(**kwargs):
    return inst(ALU.FCnvExp2F, **kwargs)

def fgetfint(**kwargs):
    return inst(ALU.FGetFInt, **kwargs)

def fgetffrac(**kwargs):
    return inst(ALU.FGetFFrac, **kwargs)

def fcnvsint2f(**kwargs):
    return inst(ALU.FCnvInt2F, signed=Signed.signed, **kwargs)

def fcnvuint2f(**kwargs):
    return inst(ALU.FCnvInt2F, signed=Signed.unsigned, **kwargs)


def and_(**kwargs):
    return inst(ALU.And, **kwargs)

def or_(**kwargs):
    return inst(ALU.Or, **kwargs)

def xor(**kwargs):
    return inst(ALU.XOr, **kwargs)

def lsl(**kwargs):
    return inst(ALU.SHL, **kwargs)

def lsr(**kwargs):
    return inst(ALU.SHR, **kwargs)

def asr(**kwargs):
    return inst(ALU.SHR, signed=Signed.signed, **kwargs)

def sel(**kwargs):
    return inst(ALU.Sel, **kwargs)

def abs(**kwargs):
    return inst(ALU.Abs, signed=Signed.signed, **kwargs)

def umin(**kwargs):
    return inst(ALU.LTE_Min, cond=Cond.ALU, **kwargs)

def umax(**kwargs):
    return inst(ALU.GTE_Max, cond=Cond.ALU, **kwargs)

def smin(**kwargs):
    return inst(ALU.LTE_Min, signed=Signed.signed, cond=Cond.ALU, **kwargs)

def smax(**kwargs):
    return inst(ALU.GTE_Max, signed=Signed.signed, cond=Cond.ALU, **kwargs)

def eq(**kwargs):
    return inst(ALU.Sub, cond=Cond.Z, **kwargs)

def ne(**kwargs):
    return inst(ALU.Sub, cond=Cond.Z_n, **kwargs)

def ult(**kwargs):
    return inst(ALU.Sub, cond=Cond.ULT, **kwargs)

def ule(**kwargs):
    return inst(ALU.Sub, cond=Cond.ULE, **kwargs)

def ugt(**kwargs):
    return inst(ALU.Sub, cond=Cond.UGT, **kwargs)

def uge(**kwargs):
    return inst(ALU.Sub, cond=Cond.UGE, **kwargs)

def slt(**kwargs):
    return inst(ALU.Sub, cond=Cond.SLT, **kwargs)

def sle(**kwargs):
    return inst(ALU.Sub, cond=Cond.SLE, **kwargs)

def sgt(**kwargs):
    return inst(ALU.Sub, cond=Cond.SGT, **kwargs)

def sge(**kwargs):
    return inst(ALU.Sub, cond=Cond.SGE, **kwargs)

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

