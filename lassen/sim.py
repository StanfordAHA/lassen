from hwtypes import BitVector, SIntVector, overflow, TypeFamily
from peak import Peak, name_outputs
from .mode import Mode, RegisterMode
from .lut import Bit, LUT, lut
from .cond import Cond, cond
from .isa import *
from .bfloat import BFloat16
import struct
import numpy as np

# simulate the PE ALU
#
#   inputs
#
#   alu is the ALU operations
#   signed is whether the inputs are unsigned or signed
#   a, b - 16-bit operands
#   d - 1-bit operatnd
#
#
#   returns res, res_p, Z, N, C, V
#
#   res - 16-bit result
#   res_p - 1-bit result
#   Z (result is 0)
#   N (result is negative)
#   C (carry generated)
#   V (overflow generated)
#
def gen_alu(family: TypeFamily):
    Bit = family.Bit
    Data = family.BitVector[DATAWIDTH]

    @name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
    def alu(inst:Inst, a:Data, b:Data, d:Bit):
        signed = inst.signed
        alu = inst.alu
    
        if signed:
            a = SIntVector(a)
            b = SIntVector(b)
            mula, mulb = a.sext(16), b.sext(16)
        else:
            mula, mulb = a.zext(16), b.zext(16)
    
        mul = mula * mulb
    
        C = Bit(0)
        V = Bit(0)
        if   alu == ALU.Add:
            res, C = a.adc(b, Bit(0))
            V = overflow(a, b, res)
            res_p = C
        elif alu == ALU.Sub:
            b_not = ~b
            res, C = a.adc(b_not, Bit(1)) 
            V = overflow(a, b_not, res)
            res_p = C
        elif alu == ALU.Mult0:
            res, C, V = mul[:16], Bit(0), Bit(0) # wrong C, V
            res_p = C
        elif alu == ALU.Mult1:
            res, C, V = mul[8:24], Bit(0), Bit(0) # wrong C, V
            res_p = C
        elif alu == ALU.Mult2:
            res, C, V = mul[16:32], Bit(0), Bit(0) # wrong C, V
            res_p = C
        elif alu == ALU.GTE_Max:
            # C, V = a-b?
            pred = a >= b
            res, res_p = pred.ite(a,b), a >= b
        elif alu == ALU.LTE_Min:
            # C, V = a-b?
            pred = a <= b
            res, res_p = pred.ite(a,b), a >= b
        elif alu == ALU.Abs:
            pred = a >= 0
            res, res_p = pred.ite(a,-a), Bit(a[-1])
        elif alu == ALU.Sel:
            res, res_p = d.ite(a,b), Bit(0)
        elif alu == ALU.And:
            res, res_p = a & b, Bit(0)
        elif alu == ALU.Or:
            res, res_p = a | b, Bit(0)
        elif alu == ALU.XOr:
            res, res_p = a ^ b, Bit(0)
        elif alu == ALU.SHR:
            res, res_p = a >> Data(b[:4]), Bit(0)
        elif alu == ALU.SHL:
            res, res_p = a << Data(b[:4]), Bit(0)
        elif alu == ALU.FP_add:
            a = BFloat16(a)
            b = BFloat16(b)
            res = a + b
            res_p = Bit(0)
        elif alu == ALU.FP_mult:
            a = BFloat16(a)
            b = BFloat16(b)
            res = a * b
            res_p = Bit(0)
        elif alu == ALU.FGetMant:
            res, res_p = (a & 0x7F), Bit(0)
        elif alu == ALU.FAddIExp:
            sign = BitVector((a & 0x8000),16)
            exp = BitVector(((a & 0x7F80)>>7),8)
            exp_check = BitVector(exp,9)
            exp += SIntVector(b[0:8])
            exp_check += SIntVector(b[0:9])
            exp_shift = BitVector(exp,16)
            exp_shift = exp_shift << 7
            mant = BitVector((a & 0x7F),16);
            res, res_p = (sign | exp_shift | mant), (exp_check > 255)
        elif alu == ALU.FSubExp:
            signa = BitVector((a & 0x8000),16)
            expa = BitVector(((a & 0x7F80)>>7),8)
            expb = BitVector(((b & 0x7F80)>>7),8)
            expa = (expa - expb + 127) 
            exp_shift = BitVector(expa,16)
            exp_shift = exp_shift << 7
            manta = BitVector((a & 0x7F),16);
            res, res_p = (signa | exp_shift | manta), Bit(0)
        elif alu == ALU.FCnvExp2F:
            biased_exp = SIntVector(((a & 0x7F80)>>7),8)
            unbiased_exp = biased_exp - SIntVector[8](127)
            if (unbiased_exp<0):
              sign=BitVector(0x8000,16)
              abs_exp=~unbiased_exp+1
            else:
              sign=BitVector(0x0000,16)
              abs_exp=unbiased_exp
            scale=-127
            for bit_pos in range(8):
              if (abs_exp[bit_pos]==Bit(1)):
                scale = bit_pos
            if (scale>=0):
              normmant = BitVector((abs_exp * (2**(7-scale))) & 0x7F,16)
            else:
              normmant = BitVector(0,16)
            biased_scale = scale + 127
            res, res_p = (sign | ((biased_scale<<7) & (0xFF<<7)) | normmant), Bit(0)
        elif alu == ALU.FGetFInt:
            signa = BitVector((a & 0x8000),16)
            expa = BitVector(((a & 0x7F80)>>7),8)
            manta = BitVector((a & 0x7F),16) | 0x80;
    
            unbiased_exp = SIntVector(expa) - SIntVector[8](127)
            if (unbiased_exp<0):
              manta_shift = BitVector(0,16)
            else:
              manta_shift = BitVector(manta,16) << BitVector[16](unbiased_exp)
            #We are not checking for overflow when converting to int
            res, res_p = (manta_shift>>7), Bit(0)
        elif alu == ALU.FGetFFrac:
            signa = BitVector((a & 0x8000),16)
            expa = BitVector(((a & 0x7F80)>>7),8)
            manta = BitVector((a & 0x7F),16) | 0x80;
    
            unbiased_exp = SIntVector(expa) - SIntVector[8](127)
            if (unbiased_exp<0):
              manta_shift = BitVector(manta,16) >> BitVector[16](-unbiased_exp)
            else:
              manta_shift = BitVector(manta,16) << BitVector[16](unbiased_exp)
            #We are not checking for overflow when converting to int
            res, res_p = ((manta_shift & 0x07F)<<1), Bit(0)
        else:
            raise NotImplementedError(alu)
    
        Z = res == 0
        N = Bit(res[-1])
    
        return res, res_p, Z, N, C, V
    return alu

class PE(Peak):

    def __init__(self):
        # Declare PE state

        # Data registers
        self.rega = RegisterMode(Data)
        self.regb = RegisterMode(Data)

        # Bit Registers
        self.regd = RegisterMode(Bit)
        self.rege = RegisterMode(Bit)
        self.regf = RegisterMode(Bit) 

    def __call__(self, inst: Inst, \
        data0: Data, data1: Data = Data(0), \
        bit0: Bit = Bit(0), bit1: Bit = Bit(0), bit2: Bit = Bit(0), \
        clk_en: Bit = Bit(1)):

        # Simulate one clock cycle

        ra = self.rega(inst.rega, inst.data0, data0, clk_en)
        rb = self.regb(inst.regb, inst.data1, data1, clk_en)

        rd = self.regd(inst.regd, inst.bit0, bit0, clk_en)
        re = self.rege(inst.rege, inst.bit1, bit1, clk_en)
        rf = self.regf(inst.regf, inst.bit2, bit2, clk_en)

        # calculate alu results
        alu = gen_alu(BitVector.get_family())
        alu_res, alu_res_p, Z, N, C, V = alu(inst, ra, rb, rd)

        # calculate lut results
        lut_res = lut(inst.lut, rd, re, rf)

        # calculate 1-bit result
        res_p = cond(inst.cond, alu_res, lut_res, Z, N, C, V)

        # calculate interrupt request 
        irq = Bit(0) # NYI

        # return 16-bit result, 1-bit result, irq
        return alu_res, res_p, irq 
