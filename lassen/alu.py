from peak import Peak, name_outputs, family_closure, Const
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH, BFloat16_fc
from hwtypes.adt import Enum
from hwtypes import BitVector, Bit as BitPy


class ALU_t(Enum):
    Adc = 0
    Sbc = 1
    Abs = 2
    Sel = 3
    Mult0 = 4
    Mult1 = 5
    Mult2 = 6
    SHR = 7
    SHL = 8
    Or = 9
    And = 10
    XOr = 11
    MULADD = 12
    MULSUB = 13
    TAA = 14
    TAS = 15
    TSA = 16
    TSS = 17
    CROP = 18
    MULSHR = 19


class Signed_t(Enum):
    unsigned = 0
    signed = 1


def overflow(a, b, res):
    msb_a = a[-1]
    msb_b = b[-1]
    N = res[-1]
    return (msb_a & msb_b & ~N) | (~msb_a & ~msb_b & N)


@family_closure
def ALU_fc(family):

    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit
    SInt = family.Signed
    SData = SInt[DATAWIDTH]
    UInt = family.Unsigned
    UData = UInt[DATAWIDTH]
    UData32 = UInt[32]

    DataPy = BitVector[DATAWIDTH]

    @family.assemble(locals(), globals(), set_port_names=True)
    class ALU(Peak):
        @name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
        def __call__(
            self,
            alu: Const(ALU_t),
            signed_: Const(Signed_t),
            a: DataPy,
            b: DataPy,
            c: DataPy,
            d: BitPy,
        ) -> (DataPy, BitPy, BitPy, BitPy, BitPy, BitPy):

            # MUL
            if signed_ == Signed_t.signed:
                mula = UData32(SData(a).sext(16))
                mulb = UData32(SData(b).sext(16))
            else:  # signed_ == Signed_t.unsigned:
                mula = UData(a).zext(16)
                mulb = UData(b).zext(16)
            mul = mula * mulb

            # LTE and min
            if signed_ == Signed_t.signed:
                lte_pred = SData(a) <= SData(b)
            else:
                lte_pred = UData(a) <= UData(b)
            min_ab = lte_pred.ite(a, b)

            # CROP (min -> max)
            if alu == ALU_t.CROP:
                max_in0 = min_ab
            else:
                max_in0 = b

            # GTE and min
            if signed_ == Signed_t.signed:
                gte_pred = SData(max_in0) >= SData(c)
            else:
                gte_pred = UData(max_in0) >= UData(c)
            max_bc = gte_pred.ite(max_in0, c)

            # mulshift
            if alu == ALU_t.MULSHR:
                shr_in0 = mul[:16]
            else:
                shr_in0 = a

            if signed_ == Signed_t.signed:
                shr = Data(SData(shr_in0) >> SData(c))
            else:  # signed_ == Signed_t.unsigned:
                shr = Data(UData(shr_in0) >> UData(c))

            if (alu == ALU_t.Sbc) | (alu == ALU_t.TSA) | (alu == ALU_t.TSS):
                b = ~b

            Cin = d

            # factor out comman add
            adder_res, adder_C = UData(a).adc(UData(b), Cin)

            # second adder
            # 1st input
            if (
                (alu == ALU_t.TAA)
                | (alu == ALU_t.TAS)
                | (alu == ALU_t.TSA)
                | (alu == ALU_t.TSS)
            ):
                adder2_in0 = adder_res
            else:
                adder2_in0 = mul[:16]

            # 2nd input
            if (alu == ALU_t.MULSUB) | (alu == ALU_t.TAS) | (alu == ALU_t.TSS):
                adder2_in1 = ~c
                Cin2 = Bit(1)
            else:
                adder2_in1 = c
                Cin2 = Bit(0)

            adder2_res, adder2_C = UData(adder2_in0).adc(adder2_in1, Cin2)

            C = Bit(0)
            V = Bit(0)
            if (alu == ALU_t.Adc) | (alu == ALU_t.Sbc):
                res, C = adder_res, adder_C
                V = overflow(a, b, res)
                res_p = C
            elif alu == ALU_t.Mult0:
                res, C, V = mul[:16], Bit(0), Bit(0)
                res_p = C
            elif alu == ALU_t.Mult1:
                res, C, V = mul[8:24], Bit(0), Bit(0)
                res_p = C
            elif alu == ALU_t.Mult2:
                res, C, V = mul[16:32], Bit(0), Bit(0)
                res_p = C
            elif alu == ALU_t.Abs:
                abs_pred = SData(a) >= SData(0)
                res, res_p = abs_pred.ite(a, UInt[16](-SInt[16](a))), Bit(a[-1])
            elif alu == ALU_t.Sel:
                res, res_p = d.ite(a, b), Bit(0)
            elif alu == ALU_t.And:
                res, res_p = a & b, Bit(0)
            elif alu == ALU_t.Or:
                res, res_p = a | b, Bit(0)
            elif alu == ALU_t.XOr:
                res, res_p = a ^ b, Bit(0)
            elif alu == ALU_t.SHR:
                res, res_p = shr, Bit(0)
            elif alu == ALU_t.SHL:
                res, res_p = a << b, Bit(0)
            elif (
                (alu == ALU_t.MULADD)
                | (alu == ALU_t.MULSUB)
                | (alu == ALU_t.TAA)
                | (alu == ALU_t.TSA)
                | (alu == ALU_t.TAS)
                | (alu == ALU_t.TSS)
            ):
                res, res_p = adder2_res, Bit(0)
            elif alu == ALU_t.CROP:
                res, res_p = max_bc, Bit(0)
            else:  # (alu == ALU_t.MULSHR):
                res, res_p = shr, Bit(0)

            N = Bit(res[-1])
            Z = res == SData(0)

            return res, res_p, Z, N, C, V

    return ALU
