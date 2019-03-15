from hwtypes import overflow, TypeFamily
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
class ALU(Peak):
    def __init__(self,family: TypeFamily, datawidth=16):
        self.Bit = family.Bit
        self.Data = family.BitVector[datawidth]
        self.Signed = family.Signed
        self.BitVector = family.BitVector

    def __call__(self,inst:Inst, a:Data, b:Data, d:Bit):
        signed = inst.signed
        alu = inst.alu
        
        a + b
        if signed:
            a = self.Signed(a)
            b = self.Signed(b)
            mula, mulb = a.sext(16), b.sext(16)
        else:
            mula, mulb = a.zext(16), b.zext(16)
    
        #print(mula, mulb, type(mula),type(mulb))
        mul = mula * mulb
    
        C = self.Bit(0)
        V = self.Bit(0)
        if   alu == ALUOP.Add:
            res, C = a.adc(b, self.Bit(0))
            V = overflow(a, b, res)
            res_p = C
        elif alu == ALUOP.Sub:
            b_not = ~b
            res, C = a.adc(b_not, self.Bit(1)) 
            V = overflow(a, b_not, res)
            res_p = C
        elif alu == ALUOP.Mult0:
            res, C, V = mul[:16], self.Bit(0), self.Bit(0) # wrong C, V
            res_p = C
        elif alu == ALUOP.Mult1:
            res, C, V = mul[8:24], self.Bit(0), self.Bit(0) # wrong C, V
            res_p = C
        elif alu == ALUOP.Mult2:
            res, C, V = mul[16:32], self.Bit(0), self.Bit(0) # wrong C, V
            res_p = C
        elif alu == ALUOP.GTE_Max:
            # C, V = a-b?
            pred = a >= b
            res, res_p = pred.ite(a,b), a >= b
        elif alu == ALUOP.LTE_Min:
            # C, V = a-b?
            pred = a <= b
            res, res_p = pred.ite(a,b), a >= b
        elif alu == ALUOP.Abs:
            pred = a >= 0
            res, res_p = pred.ite(a,-a), self.Bit(a[-1])
        elif alu == ALUOP.Sel:
            res, res_p = d.ite(a,b), self.Bit(0)
        elif alu == ALUOP.And:
            res, res_p = a & b, self.Bit(0)
        elif alu == ALUOP.Or:
            res, res_p = a | b, self.Bit(0)
        elif alu == ALUOP.XOr:
            res, res_p = a ^ b, self.Bit(0)
        elif alu == ALUOP.SHR:
            res, res_p = a >> self.Data(b[:4]), self.Bit(0)
        elif alu == ALUOP.SHL:
            res, res_p = a << self.Data(b[:4]), self.Bit(0)
        elif alu == ALUOP.FP_add:
            a = BFloat16(a)
            b = BFloat16(b)
            res = a + b
            res_p = self.Bit(0)
        elif alu == ALUOP.FP_mult:
            a = BFloat16(a)
            b = BFloat16(b)
            res = a * b
            res_p = self.Bit(0)
        elif alu == ALUOP.FGetMant:
            res, res_p = (a & 0x7F), self.Bit(0)
        elif alu == ALUOP.FAddIExp:
            sign = self.BitVector((a & 0x8000),16)
            exp = self.BitVector(((a & 0x7F80)>>7),8)
            exp_check = self.BitVector(exp,9)
            exp += self.Signed(b[0:8])
            exp_check += self.Signed(b[0:9])
            exp_shift = self.BitVector(exp,16)
            exp_shift = exp_shift << 7
            mant = self.BitVector((a & 0x7F),16);
            res, res_p = (sign | exp_shift | mant), (exp_check > 255)
        elif alu == ALUOP.FSubExp:
            signa = self.BitVector((a & 0x8000),16)
            expa = self.BitVector(((a & 0x7F80)>>7),8)
            expb = self.BitVector(((b & 0x7F80)>>7),8)
            expa = (expa - expb + 127) 
            exp_shift = self.BitVector(expa,16)
            exp_shift = exp_shift << 7
            manta = self.BitVector((a & 0x7F),16);
            res, res_p = (signa | exp_shift | manta), self.Bit(0)
        elif alu == ALUOP.FCnvExp2F:
            biased_exp = self.Signed(((a & 0x7F80)>>7),8)
            unbiased_exp = biased_exp - self.Signed[8](127)
            if (unbiased_exp<0):
              sign=self.BitVector(0x8000,16)
              abs_exp=~unbiased_exp+1
            else:
              sign=self.BitVector(0x0000,16)
              abs_exp=unbiased_exp
            scale=-127
            for bit_pos in range(8):
              if (abs_exp[bit_pos]==self.Bit(1)):
                scale = bit_pos
            if (scale>=0):
              normmant = self.BitVector((abs_exp * (2**(7-scale))) & 0x7F,16)
            else:
              normmant = self.BitVector(0,16)
            biased_scale = scale + 127
            res, res_p = (sign | ((biased_scale<<7) & (0xFF<<7)) | normmant), self.Bit(0)
        elif alu == ALUOP.FGetFInt:
            signa = self.BitVector((a & 0x8000),16)
            expa = self.BitVector(((a & 0x7F80)>>7),8)
            manta = self.BitVector((a & 0x7F),16) | 0x80;
    
            unbiased_exp = self.Signed(expa) - self.Signed[8](127)
            if (unbiased_exp<0):
              manta_shift = self.BitVector(0,16)
            else:
              manta_shift = self.BitVector(manta,16) << self.BitVector[16](unbiased_exp)
            #We are not checking for overflow when converting to int
            res, res_p = (manta_shift>>7), self.Bit(0)
        elif alu == ALUOP.FGetFFrac:
            signa = self.BitVector((a & 0x8000),16)
            expa = self.BitVector(((a & 0x7F80)>>7),8)
            manta = self.BitVector((a & 0x7F),16) | 0x80;
    
            unbiased_exp = self.Signed(expa) - self.Signed[8](127)
            if (unbiased_exp<0):
              manta_shift = self.BitVector(manta,16) >> self.BitVector[16](-unbiased_exp)
            else:
              manta_shift = self.BitVector(manta,16) << self.BitVector[16](unbiased_exp)
            #We are not checking for overflow when converting to int
            res, res_p = ((manta_shift & 0x07F)<<1), self.Bit(0)
        else:
            raise NotImplementedError(alu)
    
        Z = res == 0
        N = self.Bit(res[-1])
    
        return res, res_p, Z, N, C, V
    
class PE(Peak):

    def __init__(self,family: TypeFamily, datawidth=16):
        self.Bit = family.Bit
        self.Data = family.BitVector[datawidth]
        self.SIntVector = family.Signed
        self.BitVector = family.BitVector
        
        # Declare PE state
        self.alu = ALU(family,datawidth)
        # Data registers
        self.rega = RegisterMode(Data)
        self.regb = RegisterMode(Data)

        # Bit Registers
        self.regd = RegisterMode(Bit)
        self.rege = RegisterMode(Bit)
        self.regf = RegisterMode(Bit) 

    @name_outputs(alu_res=Data, res_p=Bit, irq=Bit)
    def __call__(self, inst: Inst, \
        data0: Data, data1: Data = None, \
        bit0: Bit = None, bit1: Bit = None, bit2: Bit = None, \
        clk_en: Bit = None):
        
        if data1 is None: data1 = self.Data(0)
        if bit0 is None: bit0 = self.Bit(0)
        if bit1 is None: bit1 = self.Bit(0)
        if bit2 is None: bit2 = self.Bit(0)
        if clk_en is None: clk_en = self.Bit(1)
        
 

        # Simulate one clock cycle

        ra = self.rega(inst.rega, inst.data0, data0, clk_en)
        rb = self.regb(inst.regb, inst.data1, data1, clk_en)

        rd = self.regd(inst.regd, inst.bit0, bit0, clk_en)
        re = self.rege(inst.rege, inst.bit1, bit1, clk_en)
        rf = self.regf(inst.regf, inst.bit2, bit2, clk_en)

        # calculate alu results
        alu_res, alu_res_p, Z, N, C, V = self.alu(inst, ra, rb, rd)

        # calculate lut results
        lut_res = lut(inst.lut, rd, re, rf)

        # calculate 1-bit result
        res_p = cond(inst.cond, alu_res, lut_res, Z, N, C, V)

        # calculate interrupt request 
        irq = self.Bit(0) # NYI

        # return 16-bit result, 1-bit result, irq
        return alu_res, res_p, irq 
