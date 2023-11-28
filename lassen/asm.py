from hwtypes import BitVector, Bit
from peak.family import PyFamily

from .isa import Inst_fc

Inst = Inst_fc(PyFamily())
LUT_t = Inst.lut
Cond_t = Inst.cond
Mode_t = Inst.rega
Op_t = Inst.op
ALU_t = Op_t.alu
FPU_t = Op_t.fpu
FPCustom_t = Op_t.fp_custom
Signed_t = Inst.signed
DataConst = Inst.data0
BitConst = Inst.bit0

# Lut Constants
B0 = BitVector[8]([0, 1, 0, 1, 0, 1, 0, 1])
B1 = BitVector[8]([0, 0, 1, 1, 0, 0, 1, 1])
B2 = BitVector[8]([0, 0, 0, 0, 1, 1, 1, 1])


def inst(
    alu,
    signed=Signed_t.unsigned,
    lut=0,
    cond=Cond_t.Z,
    ra_mode=Mode_t.BYPASS,
    ra_const=0,
    rb_mode=Mode_t.BYPASS,
    rb_const=0,
    rc_mode=Mode_t.BYPASS,
    rc_const=0,
    rd_mode=Mode_t.BYPASS,
    rd_const=0,
    re_mode=Mode_t.BYPASS,
    re_const=0,
    rf_mode=Mode_t.BYPASS,
    rf_const=0,
):

    return Inst(
        alu,
        signed,
        LUT_t(lut),
        cond,
        Mode_t(ra_mode),
        DataConst(ra_const),
        Mode_t(rb_mode),
        DataConst(rb_const),
        Mode_t(rc_mode),
        DataConst(rc_const),
        Mode_t(rd_mode),
        BitConst(rd_const),
        Mode_t(re_mode),
        BitConst(re_const),
        Mode_t(rf_mode),
        BitConst(rf_const),
    )


# helper functions to format configurations


def add(**kwargs):
    return inst(Op_t(alu=ALU_t.Adc), rd_mode=Mode_t.CONST, rd_const=0, **kwargs)


def sub(**kwargs):
    return inst(Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, **kwargs)


def adc(**kwargs):
    return inst(Op_t(alu=ALU_t.Adc), **kwargs)


def sbc(**kwargs):
    return inst(Op_t(alu=ALU_t.Sbc), **kwargs)


def taa(**kwargs):
    return inst(Op_t(alu=ALU_t.TAA), rd_mode=Mode_t.CONST, rd_const=0, **kwargs)


def tas(**kwargs):
    return inst(Op_t(alu=ALU_t.TAS), rd_mode=Mode_t.CONST, rd_const=0, **kwargs)


def tsa(**kwargs):
    return inst(Op_t(alu=ALU_t.TSA), rd_mode=Mode_t.CONST, rd_const=1, **kwargs)


def tss(**kwargs):
    return inst(Op_t(alu=ALU_t.TSS), rd_mode=Mode_t.CONST, rd_const=1, **kwargs)


def muladd(**kwargs):
    return inst(Op_t(alu=ALU_t.MULADD), **kwargs)


def mulsub(**kwargs):
    return inst(Op_t(alu=ALU_t.MULSUB), **kwargs)


def neg(**kwargs):
    return inst(Op_t(alu=ALU_t.Sbc), **kwargs)


def umult0(**kwargs):
    return inst(Op_t(alu=ALU_t.Mult0), **kwargs)


def umult1(**kwargs):
    return inst(Op_t(alu=ALU_t.Mult1), **kwargs)


def umult2(**kwargs):
    return inst(Op_t(alu=ALU_t.Mult2), **kwargs)


def smult0(**kwargs):
    return inst(Op_t(alu=ALU_t.Mult0), signed=Signed_t.signed, **kwargs)


def smult1(**kwargs):
    return inst(Op_t(alu=ALU_t.Mult1), signed=Signed_t.signed, **kwargs)


def smult2(**kwargs):
    return inst(Op_t(alu=ALU_t.Mult2), signed=Signed_t.signed, **kwargs)


def fgetmant(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FGetMant), **kwargs)


def fp_add(**kwargs):
    return inst(Op_t(fpu=FPU_t.FP_add), **kwargs)


def fp_sub(**kwargs):
    return inst(Op_t(fpu=FPU_t.FP_sub), **kwargs)


def fp_mul(**kwargs):
    return inst(Op_t(fpu=FPU_t.FP_mul), **kwargs)


def fp_cmp(cond, **kwargs):
    return inst(Op_t(fpu=FPU_t.FP_cmp), cond=cond, **kwargs)

def fp_max(**kwargs):
    return inst(Op_t(fpu=FPU_t.FP_max), **kwargs)

def fp_relu(**kwargs):
    return inst(Op_t(fpu=FPU_t.FP_max), rb_mode=Mode_t.CONST, rb_const=0, **kwargs)

def fp_gt(**kwargs):
    return fp_cmp(Cond_t.FP_GT, **kwargs)


def fp_ge(**kwargs):
    return fp_cmp(Cond_t.FP_GE, **kwargs)


def fp_lt(**kwargs):
    return fp_cmp(Cond_t.FP_LT, **kwargs)


def fp_le(**kwargs):
    return fp_cmp(Cond_t.FP_LE, **kwargs)


def fp_eq(**kwargs):
    return fp_cmp(Cond_t.FP_EQ, **kwargs)


def fp_neq(**kwargs):
    return fp_cmp(Cond_t.FP_NE, **kwargs)


def faddiexp(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FAddIExp), **kwargs)


def fsubexp(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FSubExp), **kwargs)

 
def fcnvexp2f(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FCnvExp2F), **kwargs)


def fgetfint(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FGetFInt), **kwargs)


def fgetffrac(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FGetFFrac), **kwargs)


def fcnvsint2f(**kwargs):
    return inst(Op_t(fp_custom=FPCustom_t.FCnvInt2F), signed=Signed_t.signed, **kwargs)


def fcnvuint2f(**kwargs):
    return inst(
        Op_t(fp_custom=FPCustom_t.FCnvInt2F), signed=Signed_t.unsigned, **kwargs
    )


def and_(**kwargs):
    return inst(Op_t(alu=ALU_t.And), **kwargs)


def or_(**kwargs):
    return inst(Op_t(alu=ALU_t.Or), **kwargs)


def xor(**kwargs):
    return inst(Op_t(alu=ALU_t.XOr), **kwargs)


def lsl(**kwargs):
    return inst(Op_t(alu=ALU_t.SHL), **kwargs)


def lsr(**kwargs):
    return inst(Op_t(alu=ALU_t.SHR), signed=Signed_t.unsigned, **kwargs)


def asr(**kwargs):
    return inst(Op_t(alu=ALU_t.SHR), signed=Signed_t.signed, **kwargs)


def mulshr(**kwargs):
    return inst(Op_t(alu=ALU_t.MULSHR), **kwargs)


def sel(**kwargs):
    return inst(Op_t(alu=ALU_t.Sel), **kwargs)


def abs(**kwargs):
    return inst(Op_t(alu=ALU_t.Abs), signed=Signed_t.signed, **kwargs)


def crop(**kwargs):
    return inst(Op_t(alu=ALU_t.CROP), cond=Cond_t.ALU, **kwargs)


def umin(**kwargs):
    return inst(Op_t(alu=ALU_t.CROP), cond=Cond_t.ALU, **kwargs)


def umax(**kwargs):
    return inst(Op_t(alu=ALU_t.CROP), ra_mode=Mode_t.CONST, ra_const=10, rc_mode=Mode_t.CONST, rc_const=0, cond=Cond_t.ALU, **kwargs)


def smin(**kwargs):
    return inst(Op_t(alu=ALU_t.CROP), signed=Signed_t.signed, cond=Cond_t.ALU, **kwargs)


def smax(**kwargs):
    return inst(Op_t(alu=ALU_t.CROP), ra_mode=Mode_t.CONST, ra_const=32767, rc_mode=Mode_t.CONST, rc_const=0, signed=Signed_t.signed, cond=Cond_t.ALU, **kwargs)

def eq(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.Z, **kwargs
    )


def ne(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.Z_n, **kwargs
    )


def ult(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.ULT, **kwargs
    )


def ule(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.ULE, **kwargs
    )


def ugt(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.UGT, **kwargs
    )


def uge(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.UGE, **kwargs
    )


def slt(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.SLT, **kwargs
    )


def sle(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.SLE, **kwargs
    )


def sgt(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.SGT, **kwargs
    )


def sge(**kwargs):
    return inst(
        Op_t(alu=ALU_t.Sbc), rd_mode=Mode_t.CONST, rd_const=1, cond=Cond_t.SGE, **kwargs
    )


# implements a constant using a register and add by zero
def const(val):
    return inst(
        Op_t(alu=ALU_t.Adc),
        ra_mode=Mode_t.CONST,
        ra_const=val,
        rb_mode=Mode_t.CONST,
        rb_const=0,
    )


def lut(val):
    return inst(Op_t(alu=ALU_t.Adc), lut=val, cond=Cond_t.LUT)


# Using bit1 and bit2 since bit0 can be used in the ALU_t
def lut_and():
    return lut(B1 & B2)


def lut_or():
    return lut(B1 | B2)


def lut_xor():
    return lut(B1 ^ B2)


def lut_not():
    return lut(~B1)


def lut_mux():
    return lut((B2 & B1) | ((~B2) & B0))
