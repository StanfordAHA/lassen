from peak import Peak, family_closure, name_outputs, Const
from .common import *
from .mode import gen_register_mode, gen_bit_mode
from .lut import LUT_fc
from .alu import ALU_fc
from .float.fpu import FPU_fc
from .float.float_custom import FPCustom_fc
from .cond import Cond_fc
from .isa import Inst_fc, ALU_t, FPU_t, FPCustom_t
from hwtypes import TypeFamily
from hwtypes import BitVector, Bit as BitPy


@family_closure
def PE_fc(family: TypeFamily):

    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit
    DataPy = BitVector[DATAWIDTH]

    DataReg = gen_register_mode(DATAWIDTH, 0)(family)
    BitReg = gen_bit_mode(0)(family)

    ALU = ALU_fc(family)
    FPU = FPU_fc(family)
    FPCustom = FPCustom_fc(family)

    Cond = Cond_fc(family)
    LUT = LUT_fc(family)
    Inst = Inst_fc(family)

    ALU_t_c = family.get_constructor(ALU_t)
    FPU_t_c = family.get_constructor(FPU_t)
    FPCustom_t_c = family.get_constructor(FPCustom_t)

    @family.assemble(locals(), globals(), set_port_names=False)
    class PE(Peak):
        def __init__(self):

            # Data registers
            self.rega: DataReg = DataReg()
            self.regb: DataReg = DataReg()
            self.regc: DataReg = DataReg()

            # Bit Registers
            self.regd: BitReg = BitReg()
            self.rege: BitReg = BitReg()
            self.regf: BitReg = BitReg()

            # Execution
            self.alu: ALU = ALU()
            self.fpu: FPU = FPU()
            self.fp_custom: FPCustom = FPCustom()

            # Lut
            self.lut: LUT = LUT()

            # Condition code
            self.cond: Cond = Cond()

        @name_outputs(
            res=DataPy,
            res_p=BitPy,
            reg0_config_data=DataPy,
            reg1_config_data=DataPy,
            reg2_config_data=DataPy,
        )
        def __call__(
            self,
            inst: Const(Inst),
            data0: DataPy = Data(0),
            data1: DataPy = Data(0),
            data2: DataPy = Data(0),
            bit0: BitPy = Bit(0),
            bit1: BitPy = Bit(0),
            bit2: BitPy = Bit(0),
            clk_en: Global(BitPy) = Bit(1),
        ) -> (DataPy, BitPy, DataPy, DataPy, DataPy):

            ra, ra_rdata = self.rega(inst.rega, inst.data0, data0, clk_en)
            rb, rb_rdata = self.regb(inst.regb, inst.data1, data1, clk_en)
            rc, rc_rdata = self.regc(inst.regc, inst.data2, data2, clk_en)

            rd, rd_rdata = self.regd(inst.regd, inst.bit0, bit0, clk_en)
            re, re_rdata = self.rege(inst.rege, inst.bit1, bit1, clk_en)
            rf, rf_rdata = self.regf(inst.regf, inst.bit2, bit2, clk_en)

            # set default values to each of the op kinds
            alu_op = ALU_t_c(ALU_t.Adc)
            fpu_op = FPU_t_c(FPU_t.FP_add)
            fp_custom_op = FPCustom_t_c(FPCustom_t.FGetMant)
            if inst.op.alu.match:
                alu_op = inst.op.alu.value
            elif inst.op.fpu.match:
                fpu_op = inst.op.fpu.value
            else:  # inst.op.fp_custom.match:
                fp_custom_op = inst.op.fp_custom.value

            # calculate alu results
            alu_res, alu_res_p, alu_Z, alu_N, C, alu_V = self.alu(
                alu_op, inst.signed, ra, rb, rc, rd
            )

            fpu_res, fpu_N, fpu_Z = self.fpu(fpu_op, ra, rb)

            fpc_res, fpc_res_p, fpc_V = self.fp_custom(
                fp_custom_op, inst.signed, ra, rb
            )

            Z = Bit(0)
            N = Bit(0)
            V = Bit(0)
            res_p = Bit(0)
            res = Data(0)
            if inst.op.alu.match:
                Z = alu_Z
                N = alu_N
                V = alu_V
                res_p = alu_res_p
                res = alu_res
            elif inst.op.fpu.match:
                N = fpu_N
                Z = fpu_Z
                res = fpu_res
            else:  # inst.op.fp_custom.match:
                V = fpc_V
                res_p = fpc_res_p
                res = fpc_res

            # calculate lut results
            lut_res = self.lut(inst.lut, rd, re, rf)

            # calculate 1-bit result
            cond = self.cond(inst.cond, res_p, lut_res, Z, N, C, V)

            # return 16-bit result, 1-bit result
            return res, cond, ra_rdata, rb_rdata, rc_rdata

    return PE
