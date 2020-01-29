from peak import Peak, family_closure, name_outputs, Const, assemble
from functools import lru_cache
import magma as m

from .common import *
from .mode import gen_register_mode
from .lut import LUT_fc
from .alu import ALU_fc
from .cond import Cond_fc
from .isa import Inst_fc

#Hack for now
def Global(f):
    return f

@family_closure
def PE_fc(family):
    BitVector = family.BitVector
    BV1 = family.BitVector[1]
    Data = family.BitVector[DATAWIDTH]
    Data8 = family.BitVector[8]
    Data32 = family.BitVector[32]
    Bit = family.Bit
    DataReg = gen_register_mode(Data, 0)(family)
    BitReg = gen_register_mode(Bit, 0)(family)
    ALU = ALU_fc(family)
    Cond = Cond_fc(family)
    LUT = LUT_fc(family)
    Inst = Inst_fc(family)

    @assemble(family, locals(), globals())
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

        def __call__(self, inst: Const(Inst), \
            data0: Data, data1: Data = Data(0), \
            bit0: Bit = Bit(0), bit1: Bit = Bit(0), bit2: Bit = Bit(0), \
            clk_en: Global(Bit) = Bit(1), \
            config_addr : Global(Data8) = Data8(0), \
            config_data : Global(Data32) = Data32(0), \
            config_en : Global(Bit) = Bit(0) \
        ) -> (Data, Bit, Global(Data32)):
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
                BV1(rd_rdata).concat(BV1(re_rdata)).concat(BV1(rf_rdata)).concat(BitVector[32-3](0)),
                ra_rdata.concat(rb_rdata)
            )

            # calculate alu results
            alu_res, alu_res_p, Z, N, C, V = self.alu(inst.alu, inst.signed, ra, rb, rd)

            # calculate lut results
            lut_res = self.lut(inst.lut, rd, re, rf)

            # calculate 1-bit result
            res_p = self.cond(inst.cond, alu_res_p, lut_res, Z, N, C, V)

            # return 16-bit result, 1-bit result
            return alu_res, res_p, read_config_data
    #@name_outputs(alu_res=Data,res_p=Bit,read_config_data=Global(Data32))
    return PE
