from hwtypes import BitVector, SIntVector, overflow
from peak import Peak
from .mode import Mode, RegisterMode
from .lut import Bit, LUT, lut
from .cond import Cond, cond
from .isa import *
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
def alu(alu:ALU, signed:Signed, a:Data, b:Data, d:Bit):

    if signed:
        a = SIntVector(a)
        b = SIntVector(b)
        mula, mulb = a.sext(16), b.sext(16)
    else:
        mula, mulb = a.zext(16), b.zext(16)

    mul = mula * mulb

    C = 0
    V = 0
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
    elif alu == ALU.Neg:
        if signed:
            res, res_p = ~a+Bit(1), Bit(0)
        else:
            res, res_p = ~a, Bit(0)
    elif alu == ALU.FP_add:
        raise NotImplementedError(alu)
    elif alu == ALU.FP_mult:
        raise NotImplementedError(alu)
    else:
        raise NotImplementedError(alu)

    Z = res == 0
    N = Bit(res[-1])

    return res, res_p, Z, N, C, V

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
        alu_res, alu_res_p, Z, N, C, V = alu(inst.alu, inst.signed, ra, rb, rd)

        # calculate lut results
        lut_res = lut(inst.lut, rd, re, rf)

        # calculate 1-bit result
        res_p = cond(inst.cond, alu_res, lut_res, Z, N, C, V)

        # calculate interrupt request 
        irq = Bit(0) # NYI

        # return 16-bit result, 1-bit result, irq
        return alu_res, res_p, irq

def _bv_to_bfloat(a: BitVector):
    assert (a.num_bits == 16)
    # Turn in to equivalent float32
    a_ext = BitVector.concat(a, BitVector(0, 16))
    # Change to 4 raw bytes
    raw_data = struct.pack('<I', a_ext.as_uint())
    # Re-interpret raw-bytes as np.float32
    fp = np.frombuffer(raw_data, dtype = np.float32)
    return fp
   
def _bfloat_to_bv(a: np.float32):
    # Change np.float32 to 4 raw bytes
    raw_data = struct.pack('<f', fp)
    # Re-interpret 4 raw bytes as 2 unsigned ints
    # Convert float32 to bfloat16 by taking the upper 
    # 2 bytes (chop off 16 fraction bits)
    bv_value = struct.unpack('<HH', data)[1]
    # Create BitVector from value
    bv = BitVector(bv_value, 16)
    return bv
 
