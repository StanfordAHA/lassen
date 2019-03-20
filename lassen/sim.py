from hwtypes import TypeFamily
from peak import Peak, name_outputs
from peak.auto_assembler import assemble_values_in_func
import peak.adt
from .mode import gen_register_mode
from .lut import gen_lut_type, gen_lut
from .cond import gen_cond
from .isa import *
from .family import gen_pe_type_family
import struct
import numpy as np
import magma as m

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
def gen_alu(family: TypeFamily, datawidth, assembler=None):
    Bit = family.Bit
    BitVector = family.Unsigned
    Data = family.Unsigned[datawidth]
    SInt = family.Signed
    overflow = family.overflow
    Inst = gen_inst_type(family)
    ALU = gen_alu_type(family)
    Signed = gen_signed_type(family)
    BFloat16 = family.BFloat16

    def alu(inst:Inst, a:Data, b:Data, d:Bit) -> (Data, Bit, Bit, Bit, Bit,
                                                  Bit):
        signed = inst.signed_
        alu = inst.alu
    
        if signed == Signed.signed:
            a = SInt[datawidth](a)
            b = SInt[datawidth](b)
            mula, mulb = a.sext(16), b.sext(16)
            mul = mula * mulb
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
            sign = BitVector[16]((a & 0x8000))
            exp = BitVector[8](((a & 0x7F80)>>7)[0:8])
            exp_check = exp.zext(1)
            exp = exp + b[0:8]
            exp_check = exp_check + b[0:9]
            # Augassign not supported by magma yet
            # exp += SInt[8](b[0:8])
            # exp_check += SInt[9](b[0:9])
            exp_shift = BitVector[16](exp)
            exp_shift = exp_shift << 7
            mant = BitVector[16]((a & 0x7F));
            res, res_p = (sign | exp_shift | mant), (exp_check > 255)
        elif alu == ALU.FSubExp:
            signa = BitVector[16]((a & 0x8000))
            expa = BitVector[8](((a & 0x7F80)>>7)[0:8])
            expb = BitVector[8](((b & 0x7F80)>>7)[0:8])
            expa = (expa - expb + 127)
            exp_shift = BitVector[16](expa)
            exp_shift = exp_shift << 7
            manta = BitVector[16]((a & 0x7F));
            res, res_p = (signa | exp_shift | manta), Bit(0)
        elif alu == ALU.FCnvExp2F:
            biased_exp = SInt[8](((a & 0x7F80)>>7)[0:8])
            unbiased_exp = biased_exp - SInt[8](127)
            if (unbiased_exp<0):
              sign=BitVector[16](0x8000)
              abs_exp=~unbiased_exp+1
            else:
              sign=BitVector[16](0x0000)
              abs_exp=unbiased_exp
            scale=SInt[16](-127)
            # for bit_pos in range(8):
            #   if (abs_exp[bit_pos]==Bit(1)):
            #     scale = bit_pos
            if (abs_exp[0]==Bit(1)):
              scale = SInt[16](0)
            if (abs_exp[1]==Bit(1)):
              scale = SInt[16](1)
            if (abs_exp[2]==Bit(1)):
              scale = SInt[16](2)
            if (abs_exp[3]==Bit(1)):
              scale = SInt[16](3)
            if (abs_exp[4]==Bit(1)):
              scale = SInt[16](4)
            if (abs_exp[5]==Bit(1)):
              scale = SInt[16](5)
            if (abs_exp[6]==Bit(1)):
              scale = SInt[16](6)
            if (abs_exp[7]==Bit(1)):
              scale = SInt[16](7)
            if (scale>=0):
              normmant = BitVector[16]((SInt[16](abs_exp) * (SInt[16](1) << (SInt[16](7)-scale))) & 0x7F)
            else:
              normmant = BitVector[16](0)
            biased_scale = scale + 127
            res, res_p = (sign | ((BitVector[16](biased_scale)<<7) & (0xFF<<7)) | normmant), Bit(0)
        elif alu == ALU.FGetFInt:
            signa = BitVector[16]((a & 0x8000))
            expa = BitVector[8](((a & 0x7F80)>>7)[0:8])
            manta = BitVector[16]((a & 0x7F)) | 0x80;

            unbiased_exp = SInt[8](expa) - SInt[8](127)
            if (unbiased_exp<0):
              manta_shift = BitVector[16](0)
            else:
              manta_shift = BitVector[16](manta) << BitVector[16](unbiased_exp)
            #We are not checking for overflow when converting to int
            res, res_p = (manta_shift>>7), Bit(0)
        elif alu == ALU.FGetFFrac:
            signa = BitVector[16]((a & 0x8000))
            expa = BitVector[8](((a & 0x7F80)>>7)[0:8])
            manta = BitVector[16]((a & 0x7F)) | 0x80;
    
            unbiased_exp = SInt[8](expa) - SInt[8](127)
            if (unbiased_exp<0):
              manta_shift = BitVector[16](manta) >> BitVector[16](-unbiased_exp)
            else:
              manta_shift = BitVector[16](manta) << BitVector[16](unbiased_exp)
            #We are not checking for overflow when converting to int
            res, res_p = ((manta_shift & 0x07F)<<1), Bit(0)
        #else:
        #    raise NotImplementedError(alu)
    
        Z = res == 0
        N = Bit(res[-1])
    
        return res, res_p, Z, N, C, V
    if family.Bit is m.Bit:
        alu = assemble_values_in_func(assembler, alu, locals(), globals())
        alu = m.circuit.combinational(alu)

    return alu

def gen_pe(family, assembler=None):
    family = gen_pe_type_family(family)
    alu = gen_alu(family, DATAWIDTH, assembler)
    lut = gen_lut(family)
    cond = gen_cond(family, assembler)

    Bit = family.Bit
    Data = family.BitVector[DATAWIDTH]

    DataReg = gen_register_mode(Data)
    BitReg = gen_register_mode(Bit)

    Inst = gen_inst_type(family)

    class PE(Peak):

        def __init__(self):
            # Declare PE state

            # Data registers
            self.rega: DataReg = DataReg()
            self.regb: DataReg = DataReg()

            # Bit Registers
            self.regd: BitReg = BitReg()
            self.rege: BitReg = BitReg()
            self.regf: BitReg = BitReg()

        def __call__(self, inst: Inst, \
            data0: Data, data1: Data = Data(0), \
            bit0: Bit = Bit(0), bit1: Bit = Bit(0), bit2: Bit = Bit(0), \
            clk_en: Bit = Bit(1)) -> (Data, Bit, Bit):

            # Simulate one clock cycle

            ra = self.rega(inst.rega, inst.data0, data0, clk_en)
            rb = self.regb(inst.regb, inst.data1, data1, clk_en)

            rd = self.regd(inst.regd, inst.bit0, bit0, clk_en)
            re = self.rege(inst.rege, inst.bit1, bit1, clk_en)
            rf = self.regf(inst.regf, inst.bit2, bit2, clk_en)

            # calculate alu results
            alu_res, alu_res_p, Z, N, C, V = alu(inst, ra, rb, rd)

            # calculate lut results
            lut_res = lut(inst.lut, rd, re, rf)

            # calculate 1-bit result
            res_p = cond(inst.cond, alu_res_p, lut_res, Z, N, C, V)

            # calculate interrupt request 
            irq = Bit(0) # NYI

            # return 16-bit result, 1-bit result, irq
            return alu_res, res_p, irq 
    if family.Bit is m.Bit:
        PE = m.circuit.sequential(PE)
    return PE
