import hwtypes
from hwtypes import TypeFamily
from peak import Peak, name_outputs
from peak.auto_assembler import assemble_values_in_func, generate_assembler
from .common import Global, Config
from .mode import gen_register_mode
from .lut import gen_lut_type, gen_lut
from .cond import gen_cond
from .isa import *
from .family import gen_pe_type_family
from .common import Global
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
            mula, mulb = Data(a).zext(16), Data(b).zext(16)
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
            res, C, V = mul[:16], Bit(0), Bit(0)  # wrong C, V
            res_p = C
        elif alu == ALU.Mult1:
            res, C, V = mul[8:24], Bit(0), Bit(0)  # wrong C, V
            res_p = C
        elif alu == ALU.Mult2:
            res, C, V = mul[16:32], Bit(0), Bit(0)  # wrong C, V
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
            res, res_p = d.ite(a, b), Bit(0)
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
                b = (Data(1) << (DATAWIDTH-1)) ^ b
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
            exp = BitVector[16](a)[7:15]
            exp_check = exp.zext(1)
            exp = exp + b[0:8]
            exp_check = exp_check + b[0:9]
            # Augassign not supported by magma yet
            # exp += SInt[8](b[0:8])
            # exp_check += SInt[9](b[0:9])
            exp_shift = BitVector[16](exp)
            exp_shift = exp_shift << 7
            mant = BitVector[16]((a & 0x7F))
            res, res_p = (sign | exp_shift | mant), (exp_check > 255)
        elif alu == ALU.FSubExp:
            signa = BitVector[16]((a & 0x8000))
            expa = BitVector[16](a)[7:15]
            signb = BitVector[16]((b & 0x8000))
            expb = BitVector[16](b)[7:15]
            expa = (expa - expb + 127)
            exp_shift = BitVector[16](expa)
            exp_shift = exp_shift << 7
            manta = BitVector[16]((a & 0x7F))
            res, res_p = ((signa | signb) | exp_shift | manta), Bit(0)
        elif alu == ALU.FCnvExp2F:
            expa0 = BitVector[8](a[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            if (unbiased_exp0 < 0):
                sign = BitVector[16](0x8000)
                abs_exp0 = -unbiased_exp0
            else:
                sign = BitVector[16](0x0000)
                abs_exp0 = unbiased_exp0
            abs_exp = BitVector[8](abs_exp0[0:8])
            scale = SInt[16](-127)
            # for bit_pos in range(8):
            #   if (abs_exp[bit_pos]==Bit(1)):
            #     scale = bit_pos
            if (abs_exp[0] == Bit(1)):
                scale = SInt[16](0)
            if (abs_exp[1] == Bit(1)):
                scale = SInt[16](1)
            if (abs_exp[2] == Bit(1)):
                scale = SInt[16](2)
            if (abs_exp[3] == Bit(1)):
                scale = SInt[16](3)
            if (abs_exp[4] == Bit(1)):
                scale = SInt[16](4)
            if (abs_exp[5] == Bit(1)):
                scale = SInt[16](5)
            if (abs_exp[6] == Bit(1)):
                scale = SInt[16](6)
            if (abs_exp[7] == Bit(1)):
                scale = SInt[16](7)
            if (scale >= 0):
                normmant = BitVector[16](
                    (SInt[16](abs_exp) * (SInt[16](1) << (SInt[16](7)-scale))) & 0x7F)
            else:
                normmant = BitVector[16](0)
            biased_scale = scale + 127
            res, res_p = (sign | ((BitVector[16](biased_scale) << 7) & (
                0xFF << 7)) | normmant), Bit(0)
        elif alu == ALU.FGetFInt:
            signa = BitVector[16]((a & 0x8000))
            manta = BitVector[16]((a & 0x7F)) | 0x80
            expa0 = BitVector[8](a[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
            if (unbiased_exp0 < 0):
                manta_shift0 = BitVector[23](0)
            else:
                manta_shift0 = BitVector[23](
                    manta) << BitVector[23](unbiased_exp0)
            unsigned_res0 = BitVector[23](manta_shift0 >> BitVector[23](7))
            unsigned_res = BitVector[16](unsigned_res0[0:16])
            if (signa == 0x8000):
                signed_res = SInt[16](-unsigned_res)
            else:
                signed_res = SInt[16](unsigned_res)
            # We are not checking for overflow when converting to int
            res, res_p, V = signed_res, 0, (expa0 >  BitVector[8](142))
        elif alu == ALU.FGetFFrac:
            signa = BitVector[16]((a & 0x8000))
            manta = BitVector[16]((a & 0x7F)) | 0x80
            expa0 = BitVector[8](a[7:15])
            biased_exp0 = SInt[9](expa0.zext(1))
            unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))

            if (unbiased_exp0 < 0):
                manta_shift1 = BitVector[16](
                    manta) >> BitVector[16](-unbiased_exp0)
            else:
                manta_shift1 = BitVector[16](
                    manta) << BitVector[16](unbiased_exp0)
            unsigned_res = BitVector[16]((manta_shift1 & 0x07F))
            if (signa == 0x8000):
                signed_res = SInt[16](-unsigned_res)
            else:
                signed_res = SInt[16](unsigned_res)

            # We are not checking for overflow when converting to int
            res, res_p = signed_res, Bit(0)
        elif alu == ALU.FCnvInt2F:
            if signed == Signed.signed:
                sign = BitVector[16]((a) & 0x8000)
            else:
                sign = BitVector[16](0)
            if (sign[15] == Bit(1)):
                abs_input = BitVector[16](-a)
            else:
                abs_input = BitVector[16](a)
            scale = SInt[16](-127)
            # for bit_pos in range(8):
            #   if (abs_exp[bit_pos]==Bit(1)):
            #     scale = bit_pos
            if (abs_input[0] == Bit(1)):
                scale = SInt[16](0)
            if (abs_input[1] == Bit(1)):
                scale = SInt[16](1)
            if (abs_input[2] == Bit(1)):
                scale = SInt[16](2)
            if (abs_input[3] == Bit(1)):
                scale = SInt[16](3)
            if (abs_input[4] == Bit(1)):
                scale = SInt[16](4)
            if (abs_input[5] == Bit(1)):
                scale = SInt[16](5)
            if (abs_input[6] == Bit(1)):
                scale = SInt[16](6)
            if (abs_input[7] == Bit(1)):
                scale = SInt[16](7)
            if (abs_input[8] == Bit(1)):
                scale = SInt[16](8)
            if (abs_input[9] == Bit(1)):
                scale = SInt[16](9)
            if (abs_input[10] == Bit(1)):
                scale = SInt[16](10)
            if (abs_input[11] == Bit(1)):
                scale = SInt[16](11)
            if (abs_input[12] == Bit(1)):
                scale = SInt[16](12)
            if (abs_input[13] == Bit(1)):
                scale = SInt[16](13)
            if (abs_input[14] == Bit(1)):
                scale = SInt[16](14)
            if (abs_input[15] == Bit(1)):
                scale = SInt[16](15)
            if (scale >= 0):
                normmant = BitVector[16](
                    (SInt[16](abs_input) * (SInt[16](1) << (SInt[16](15)-scale))) & 0x7F00)
            else:
                normmant = BitVector[16](0)
            biased_scale = scale + 127
            res, res_p = (sign | ((BitVector[16](biased_scale) << 7) & (
                0xFF << 7)) | (BitVector[16](normmant) >> 8), Bit(0))

        # else:
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
    BV1 = family.BitVector[1]
    Data = family.BitVector[DATAWIDTH]
    Data32 = family.BitVector[32]
    Data8 = family.BitVector[32]
    ConfigData32 = Config(family.BitVector)[32]
    ConfigData8 = Config(family.BitVector)[8]
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
            clk_en: Global(Bit) = Bit(1), \
            config_addr : Config(Data8) = Data8(0), \
            config_data : Config(Data32) = Data32(0), \
            config_en : Config(Bit) = Bit(0) \
        ) -> (Data, Bit, ConfigData32):
            # Simulate one clock cycle

            data01_addr = (config_addr[:3] == family.BitVector[3](DATA01_ADDR))
            bit012_addr = (config_addr[:3] == family.BitVector[3](BIT012_ADDR))

            #ra
            ra_we = (data01_addr & config_en)
            ra_config_wdata = config_data[DATA0_START:DATA0_START+DATA0_WIDTH]

            #rb
            rb_we = ra_we
            rb_config_wdata = config_data[DATA1_START:DATA1_START+DATA1_WIDTH]

            #rd
            rd_we = (bit012_addr & config_en)
            rd_config_wdata = config_data[BIT0_START]

            #re
            re_we = rd_we
            re_config_wdata = config_data[BIT1_START]

            #rf
            rf_we = rd_we
            rf_config_wdata = config_data[BIT2_START]

            ra, ra_rdata = self.rega(inst.rega, inst.data0, data0, clk_en, ra_we, ra_config_wdata)
            rb, rb_rdata = self.regb(inst.regb, inst.data1, data1, clk_en, rb_we, rb_config_wdata)

            rd, rd_rdata = self.regd(inst.regd, inst.bit0, bit0, clk_en, rd_we, rd_config_wdata)
            re, re_rdata = self.rege(inst.rege, inst.bit1, bit1, clk_en, re_we, re_config_wdata)
            rf, rf_rdata = self.regf(inst.regf, inst.bit2, bit2, clk_en, rf_we, rf_config_wdata)

            #Calculate read_config_data
            read_config_data = ConfigData32(ra_rdata.concat(rb_rdata))
            if bit012_addr:
                read_config_data = BV1(rd_rdata).concat(BV1(re_rdata)).concat(BV1(rf_rdata)).concat(BitVector[32-3](0))
                read_config_data = ConfigData32(read_config_data)


            # calculate alu results
            alu_res, alu_res_p, Z, N, C, V = alu(inst, ra, rb, rd)

            # calculate lut results
            lut_res = lut(inst.lut, rd, re, rf)

            # calculate 1-bit result
            res_p = cond(inst.cond, alu_res_p, lut_res, Z, N, C, V)

            # return 16-bit result, 1-bit result
            return alu_res, res_p, read_config_data
    if family.Bit is m.Bit:
        PE = m.circuit.sequential(PE)
    else:
        PE.__call__ = name_outputs(alu_res=Data,res_p=Bit,read_config_data=ConfigData32)(PE.__call__)
    return PE
