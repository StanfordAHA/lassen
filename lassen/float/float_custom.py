from hwtypes.adt import Enum
from peak import Peak, family_closure, Const, name_outputs
from ..alu import Signed_t


class FPCustom_t(Enum):
    FGetMant = 0
    FAddIExp = 1
    FSubExp = 2
    FCnvExp2F = 3
    FGetFInt = 4
    FGetFFrac = 5
    FCnvInt2F = 6


@family_closure
def FPCustom_fc(family):
    BitVector = family.BitVector
    Data = family.BitVector[16]
    Bit = family.Bit
    SInt = family.Signed
    SData = SInt[16]
    UInt = family.Unsigned
    UData = UInt[16]
    UData32 = UInt[32]

    FPExpBV = family.BitVector[8]
    FPFracBV = family.BitVector[7]

    @family.assemble(locals(), globals(), set_port_names=True)
    class FPCustom(Peak):
        @name_outputs(res=Data, res_p=Bit, V=Bit)
        def __call__(
            self, op: Const(FPCustom_t), signed_: Const(Signed_t), a: Data, b: Data
        ) -> (Data, Bit, Bit):
            if op == FPCustom_t.FCnvExp2F:
                expa0 = BitVector[8](a[7:15])
                biased_exp0 = SInt[9](expa0.zext(1))
                unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
                if unbiased_exp0 < 0:
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
                if abs_exp[0] == Bit(1):
                    scale = SInt[16](0)
                if abs_exp[1] == Bit(1):
                    scale = SInt[16](1)
                if abs_exp[2] == Bit(1):
                    scale = SInt[16](2)
                if abs_exp[3] == Bit(1):
                    scale = SInt[16](3)
                if abs_exp[4] == Bit(1):
                    scale = SInt[16](4)
                if abs_exp[5] == Bit(1):
                    scale = SInt[16](5)
                if abs_exp[6] == Bit(1):
                    scale = SInt[16](6)
                if abs_exp[7] == Bit(1):
                    scale = SInt[16](7)
                normmant_mul_left = SInt[16](abs_exp)
                normmant_mul_right = SInt[16](7) - scale
                normmant_mask = SInt[16](0x7F)
            else:  # op == FPCustom_t.FCnvInt2F:
                if signed_ == Signed_t.signed:
                    sign = BitVector[16]((a) & 0x8000)
                else:
                    sign = BitVector[16](0)
                if sign[15] == Bit(1):
                    abs_input = BitVector[16](-SInt[16](a))
                else:
                    abs_input = BitVector[16](a)
                scale = SInt[16](-127)
                # for bit_pos in range(8):
                #   if (abs_exp[bit_pos]==Bit(1)):
                #     scale = bit_pos
                if abs_input[0] == Bit(1):
                    scale = SInt[16](0)
                if abs_input[1] == Bit(1):
                    scale = SInt[16](1)
                if abs_input[2] == Bit(1):
                    scale = SInt[16](2)
                if abs_input[3] == Bit(1):
                    scale = SInt[16](3)
                if abs_input[4] == Bit(1):
                    scale = SInt[16](4)
                if abs_input[5] == Bit(1):
                    scale = SInt[16](5)
                if abs_input[6] == Bit(1):
                    scale = SInt[16](6)
                if abs_input[7] == Bit(1):
                    scale = SInt[16](7)
                if abs_input[8] == Bit(1):
                    scale = SInt[16](8)
                if abs_input[9] == Bit(1):
                    scale = SInt[16](9)
                if abs_input[10] == Bit(1):
                    scale = SInt[16](10)
                if abs_input[11] == Bit(1):
                    scale = SInt[16](11)
                if abs_input[12] == Bit(1):
                    scale = SInt[16](12)
                if abs_input[13] == Bit(1):
                    scale = SInt[16](13)
                if abs_input[14] == Bit(1):
                    scale = SInt[16](14)
                if abs_input[15] == Bit(1):
                    scale = SInt[16](15)
                normmant_mul_left = SInt[16](abs_input)
                normmant_mul_right = SInt[16](15) - scale
                normmant_mask = SInt[16](0x7F00)

            # if (op == FPCustom_t.FCnvInt2F) | (op == FPCustom_t.FCnvExp2F):
            if scale >= 0:
                normmant = BitVector[16](
                    (normmant_mul_left << normmant_mul_right) & normmant_mask
                )
            else:
                normmant = BitVector[16](0)

            if op == FPCustom_t.FCnvInt2F:
                normmant = BitVector[16](normmant) >> 8

            biased_scale = scale + 127
            to_float_result = (
                sign | ((BitVector[16](biased_scale) << 7) & (0xFF << 7)) | normmant
            )

            V = Bit(0)
            if op == FPCustom_t.FGetMant:
                res, res_p = (a & 0x7F), Bit(0)
            elif op == FPCustom_t.FAddIExp:
                sign = BitVector[16]((a & 0x8000))
                exp = UData(a)[7:15]
                exp_check = exp.zext(1)
                exp = exp + UData(b)[0:8]
                exp_check = exp_check + UData(b)[0:9]
                # Augassign not supported by magma yet
                # exp += SInt[8](b[0:8])
                # exp_check += SInt[9](b[0:9])
                exp_shift = BitVector[16](exp)
                exp_shift = exp_shift << 7
                mant = BitVector[16]((a & 0x7F))
                res, res_p = (sign | exp_shift | mant), (exp_check > 255)
            elif op == FPCustom_t.FSubExp:
                signa = BitVector[16]((a & 0x8000))
                expa = UData(a)[7:15]
                signb = BitVector[16]((b & 0x8000))
                expb = UData(b)[7:15]
                expa = expa - expb + 127
                exp_shift = BitVector[16](expa)
                exp_shift = exp_shift << 7
                manta = BitVector[16]((a & 0x7F))
                res, res_p = ((signa | signb) | exp_shift | manta), Bit(0)
            elif op == FPCustom_t.FCnvExp2F:
                res, res_p = to_float_result, Bit(0)
            elif op == FPCustom_t.FGetFInt:
                signa = BitVector[16]((a & 0x8000))
                manta = BitVector[16]((a & 0x7F)) | 0x80
                expa0 = UData(a)[7:15]
                biased_exp0 = SInt[9](expa0.zext(1))
                unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))
                if unbiased_exp0 < 0:
                    manta_shift0 = BitVector[23](0)
                else:
                    manta_shift0 = BitVector[23](manta) << BitVector[23](unbiased_exp0)
                unsigned_res0 = BitVector[23](manta_shift0 >> BitVector[23](7))
                unsigned_res = BitVector[16](unsigned_res0[0:16])
                if signa == 0x8000:
                    signed_res = -SInt[16](unsigned_res)
                else:
                    signed_res = SInt[16](unsigned_res)
                # We are not checking for overflow when converting to int
                res, res_p, V = signed_res, Bit(0), (expa0 > BitVector[8](142))
            elif op == FPCustom_t.FGetFFrac:
                signa = BitVector[16]((a & 0x8000))
                manta = BitVector[16]((a & 0x7F)) | 0x80
                expa0 = BitVector[8](a[7:15])
                biased_exp0 = SInt[9](expa0.zext(1))
                unbiased_exp0 = SInt[9](biased_exp0 - SInt[9](127))

                if unbiased_exp0 < 0:
                    manta_shift1 = BitVector[16](manta) >> BitVector[16](-unbiased_exp0)
                else:
                    manta_shift1 = BitVector[16](manta) << BitVector[16](unbiased_exp0)
                unsigned_res = BitVector[16]((manta_shift1 & 0x07F))
                if signa == 0x8000:
                    signed_res = -SInt[16](unsigned_res)
                else:
                    signed_res = SInt[16](unsigned_res)

                # We are not checking for overflow when converting to int
                res, res_p = signed_res, Bit(0)
            else:  # op == FPCustom_t.FCnvInt2F:
                res, res_p = to_float_result, Bit(0)

            return res, res_p, V

    return FPCustom
