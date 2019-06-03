import hwtypes
from hwtypes import TypeFamily
from peak import Peak, name_outputs
from peak.auto_assembler import assemble_values_in_func, generate_assembler
from .common import Global
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
def gen_alu(family: TypeFamily, datawidth, use_assembler=False):
    Bit = family.Bit
    BitVector = family.Unsigned
    Data = family.Unsigned[datawidth]
    SInt = family.Signed
    overflow = family.overflow
    Inst = gen_inst_type(family)
    ALU = gen_alu_type(family)
    Signed = gen_signed_type(family)
    BFloat16 = family.BFloat16

    FPExpBV = BitVector[8]
    FPFracBV = BitVector[7]

    def bv2float(bv):
        return BFloat16.reinterpret_from_bv(bv)

    def float2bv(bvf):
        return BFloat16.reinterpret_as_bv(bvf)

    def fp_get_exp(val : Data):
        return val[7:15]

    def fp_get_frac(val : Data):
        return val[:7]

    def fp_is_zero(val : Data):
        return (fp_get_exp(val) == FPExpBV(0)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_inf(val : Data):
        return (fp_get_exp(val) == FPExpBV(-1)) & (fp_get_frac(val) == FPFracBV(0))

    def fp_is_neg(val : Data):
        return Bit(val[-1])

    def alu(inst:Inst, a:Data, b:Data, d:Bit) -> (Data, Bit, Bit, Bit, Bit, Bit):
        signed = inst.signed_
        alu = inst.alu
        if signed == Signed.signed:
            a = SInt[datawidth](a)
            b = SInt[datawidth](b)
            mula, mulb = a.sext(16), b.sext(16)
            mul = mula * mulb
            gte_pred = a >= b
            lte_pred = a <= b
            abs_pred = a >= 0
            shr = a >> b
        elif signed == Signed.unsigned:
            mula, mulb = a.zext(16), b.zext(16)
            mul = mula * mulb
            gte_pred = a >= b
            lte_pred = a <= b
            abs_pred = a >= 0
            shr = a >> b
        a_inf = fp_is_inf(a)
        b_inf = fp_is_inf(b)
        a_neg = fp_is_neg(a)
        b_neg = fp_is_neg(b)

        Cin = Bit(0)
        if (alu == ALU.Sub) | (alu == ALU.Sbc):
            b = ~b
        if (alu == ALU.Sub):
            Cin = Bit(1)
        elif (alu == ALU.Adc) | (alu == ALU.Sbc):
            Cin = d

        C = Bit(0)
        V = Bit(0)
        if (alu == ALU.Add) | (alu == ALU.Sub) | (alu == ALU.Adc) | (alu == ALU.Sbc):
            res, C = a.adc(b, Cin)
            V = overflow(a, b, res)
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
            res, res_p = gte_pred.ite(a,b), gte_pred
        elif alu == ALU.LTE_Min:
            # C, V = a-b?
            res, res_p = lte_pred.ite(a,b), lte_pred
        elif alu == ALU.Abs:
            res, res_p = abs_pred.ite(a,-a), Bit(a[-1])
        elif alu == ALU.Sel:
            res, res_p = d.ite(a,b), Bit(0)
        elif alu == ALU.And:
            res, res_p = a & b, Bit(0)
        elif alu == ALU.Or:
            res, res_p = a | b, Bit(0)
        elif alu == ALU.XOr:
            res, res_p = a ^ b, Bit(0)
        elif alu == ALU.SHR:
            #res, res_p = a >> Data(b[:4]), Bit(0)
            res, res_p = shr, Bit(0)
        elif alu == ALU.SHL:
            #res, res_p = a << Data(b[:4]), Bit(0)
            res, res_p = a << b, Bit(0)
        elif (alu == ALU.FP_add) | (alu == ALU.FP_sub) | (alu == ALU.FP_cmp):
            #Flip the sign bit of b
            if (alu == ALU.FP_sub) | (alu == ALU.FP_cmp):
                b = BitVector.concat(b[:-1],~b[-1:])
            a = bv2float(a)
            b = bv2float(b)
            res = float2bv(a + b)
            res_p = Bit(0)
        elif alu == ALU.FP_mult:
            a = bv2float(a)
            b = bv2float(b)
            res = float2bv(a * b)
            res_p = Bit(0)
        elif alu == ALU.FGetMant:
            res, res_p = (a & 0x7F), Bit(0)
        elif alu == ALU.FAddIExp:
            sign = BitVector[16]((a & 0x8000))
            exp = a[7:15]
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
            expa = a[7:15]
            expb = b[7:15]
            expa = (expa - expb + 127)
            exp_shift = BitVector[16](expa)
            exp_shift = exp_shift << 7
            manta = BitVector[16]((a & 0x7F));
            res, res_p = (signa | exp_shift | manta), Bit(0)
        elif alu == ALU.FCnvExp2F:
            biased_exp = SInt[8](a[7:15])
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
            expa = a[7:15]
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
            expa = a[7:15]
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

        N = Bit(res[-1])
        if (alu == ALU.FP_sub) | (alu == ALU.FP_add) | (alu == ALU.FP_mult) | (alu==ALU.FP_cmp):
            Z = fp_is_zero(res)
        else:
            Z = (res == 0)

        #Nicely handles infinities for comparisons
        if (alu == ALU.FP_cmp):
            if (a_inf & b_inf) & (a_neg == b_neg):
                Z = Bit(1)

        return res, res_p, Z, N, C, V
    if family.Bit is m.Bit:
        if use_assembler:
            bv_fam = gen_pe_type_family(hwtypes.BitVector.get_family())
            bv_alu = gen_alu_type(bv_fam)
            bv_signed = gen_signed_type(bv_fam)
            assemblers = {
                ALU: (bv_alu, generate_assembler(bv_alu)[0]),
                Signed: (bv_signed, generate_assembler(bv_signed)[0])
            }
            alu = assemble_values_in_func(assemblers, alu, locals(), globals())
        alu = m.circuit.combinational(alu)

    return alu





def gen_pe(family, use_assembler=False):
    family = gen_pe_type_family(family)
    alu = gen_alu(family, DATAWIDTH, use_assembler)
    lut = gen_lut(family)
    cond = gen_cond(family, use_assembler)

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
            bit0: Bit = Bit(0), bit1: Bit = Bit(0), bit2: Bit = Bit(0)
        ) -> (Data, Bit, Global(Bit)):
            # Simulate one clock cycle

            ra = self.rega(inst.rega, inst.data0, data0)
            rb = self.regb(inst.regb, inst.data1, data1)

            rd = self.regd(inst.regd, inst.bit0, bit0)
            re = self.rege(inst.rege, inst.bit1, bit1)
            rf = self.regf(inst.regf, inst.bit2, bit2)

            # calculate alu results
            alu_res, alu_res_p, Z, N, C, V = alu(inst, ra, rb, rd)

            # calculate lut results
            lut_res = lut(inst.lut, rd, re, rf)

            # calculate 1-bit result
            res_p = cond(inst.cond, alu_res_p, lut_res, Z, N, C, V)
            # calculate interrupt request
            # TODO(rsetaluri, rdaly): Implement logic to compute irq.
            irq = Global(Bit)(0)

            # return 16-bit result, 1-bit result, irq
            return alu_res, res_p, irq
    if family.Bit is m.Bit:
        PE = m.circuit.sequential(PE)
    else:
        PE.__call__ = name_outputs(alu_res=Data,res_p=Bit,irq=Global(Bit))(PE.__call__)
    return PE
