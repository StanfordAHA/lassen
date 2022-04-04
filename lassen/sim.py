from peak import Peak, family_closure, name_outputs, Const
from .common import *
from .mode import gen_register_mode, gen_bit_mode
from .lut import LUT_fc
from .alu import ALU_fc
from .cond import Cond_fc
from .isa import Inst_fc, ALU_t
from hwtypes import TypeFamily
from hwtypes import BitVector, Bit as BitPy

@family_closure
def PE_fc(family: TypeFamily):

    #Hack
    def BV1(bit):
        return bit.ite(family.BitVector[1](1), family.BitVector[1](0))
    Data = family.BitVector[DATAWIDTH]
    Data8 = family.BitVector[8]
    Data32 = family.BitVector[32]
    Data48 = family.BitVector[48]
    Bit = family.Bit

    DataPy = BitVector[DATAWIDTH]
    Data8Py = BitVector[8]
    Data32Py = BitVector[32]
    Data48Py = BitVector[48]

    DataReg = gen_register_mode(DATAWIDTH, 0)(family)
    BitReg = gen_bit_mode(0)(family)

    ALU = ALU_fc(family)

    Cond = Cond_fc(family)
    LUT = LUT_fc(family)
    Inst = Inst_fc(family)

    ALU_t_c = family.get_constructor(ALU_t)

    @family.assemble(locals(), globals(), set_port_names=False)
    class PE(Peak):
        def __init__(self):

            # Data registers
            self.rega: DataReg = DataReg()
            self.regb: DataReg = DataReg()

            # Bit Registers
            self.regd: BitReg = BitReg()
            self.rege: BitReg = BitReg()
            self.regf: BitReg = BitReg()

            #Execution
            self.alu: ALU = ALU()

            #Lut
            self.lut: LUT = LUT()

            #Condition code
            self.cond: Cond = Cond()

        @name_outputs(res=DataPy, res_p=BitPy, read_config_data=Data32Py)
        def __call__(
            self,
            inst: Const(Inst),
            data0: DataPy,
            data1: DataPy = Data(0),
            bit0: BitPy = Bit(0),
            bit1: BitPy = Bit(0),
            bit2: BitPy = Bit(0),
            clk_en: Global(BitPy) = Bit(1),
            config_addr : Data8Py = Data8(0),
            config_data : Data32Py = Data32(0),
            config_en : BitPy = Bit(0)
        ) -> (DataPy, BitPy, Data32Py):

            data0_addr = (config_addr[:3] == family.BitVector[3](DATA0_ADDR))
            data1_addr = (config_addr[:3] == family.BitVector[3](DATA1_ADDR))
            bit012_addr = (config_addr[:3] == family.BitVector[3](BIT012_ADDR))

            #ra
            ra_we = (data0_addr & config_en)
            ra_config_wdata = config_data[DATA_START:DATA_START+DATA_WIDTH]

            #rb
            rb_we = (data1_addr & config_en)
            rb_config_wdata = config_data[DATA_START:DATA_START+DATA_WIDTH]

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


            if bit012_addr:
                read_config_data = BV1(rd_rdata).concat(BV1(re_rdata)).concat(BV1(rf_rdata)).concat(family.BitVector[32-3](0))
            elif data0_addr:
                read_config_data = ra_rdata.concat(family.BitVector[16](0))
            else: #if data1_addr:
                read_config_data = rb_rdata.concat(family.BitVector[16](0))

            #Compute the outputs

            #set default values to each of the op kinds
            alu_op = inst.alu
          
            # calculate alu results
            alu_res, alu_res_p, alu_Z, alu_N, C, alu_V = self.alu(alu_op, inst.signed, ra, rb, rd)

            Z = alu_Z
            N = alu_N
            V = alu_V
            res_p = alu_res_p
            res = alu_res

            # calculate lut results
            lut_res = self.lut(inst.lut, rd, re, rf)

            # calculate 1-bit result
            cond = self.cond(inst.cond, res_p, lut_res, Z, N, C, V)

            # return 16-bit result, 1-bit result
            return res, cond, read_config_data
    return PE
