#from peak import Peak, name_outputs
from peak import Peak
from hwtypes import BitVector, Bit

from .common import *
from .mode import gen_register_mode
from .lut import LUT
from .alu import ALU
from .cond import Cond
from .isa import Inst

BV1 = BitVector[1]

DataReg = gen_register_mode(Data, Data(0))
BitReg = gen_register_mode(Bit, Bit(0))

class PE(Peak):
    def __init__(self):

        # Data registers
        self.rega: DataReg = DataReg()
        self.regb: DataReg = DataReg()

        # Bit Registers
        self.regd: BitReg = BitReg()
        self.rege: BitReg = BitReg()
        self.regf: BitReg = BitReg()

        #ALU
        self.alu: ALU = ALU()

        #Condition code
        self.cond: Cond = Cond()

        #Lut
        self.lut: LUT = LUT()

    def __call__(self, inst: Inst, \
        data0: Data, data1: Data = Data(0), \
        bit0: Bit = Bit(0), bit1: Bit = Bit(0), bit2: Bit = Bit(0), \
        clk_en: Global(Bit) = Bit(1), \
        config_addr : ConfigData8 = ConfigData8(0), \
        config_data : ConfigData32 = ConfigData32(0), \
        config_en : Config(Bit) = Bit(0) \
    ) -> (Data, Bit, ConfigData32):
        # Simulate one clock cycle


        data01_addr = (config_addr[:3] == BitVector[3](DATA01_ADDR))
        bit012_addr = (config_addr[:3] == BitVector[3](BIT012_ADDR))

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
        read_config_data = bit012_addr.ite(
            ConfigData32(BV1(rd_rdata).concat(BV1(re_rdata)).concat(BV1(rf_rdata)).concat(BitVector[32-3](0))),
            ConfigData32(ra_rdata.concat(rb_rdata))
        )

        # calculate alu results
        alu_res, alu_res_p, Z, N, C, V = self.alu(inst.alu, inst.signed, ra, rb, rd)

        # calculate lut results
        lut_res = self.lut(inst.lut, rd, re, rf)

        # calculate 1-bit result
        res_p = self.cond(inst.cond, alu_res_p, lut_res, Z, N, C, V)

        # return 16-bit result, 1-bit result
        return alu_res, res_p, read_config_data
    #PE.__call__ = name_outputs(alu_res=Data,res_p=Bit,read_config_data=ConfigData32)(PE.__call__)
