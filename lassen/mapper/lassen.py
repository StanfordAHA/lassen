from lassen.sim import gen_pe
import lassen.asm as asm
from hwtypes import BitVector
import coreir
import metamapper as mm

ALU = asm.ALU
Cond = asm.Cond

class LassenMapper(mm.PeakMapper):
    def __init__(self,context : coreir.context):
        super(LassenMapper,self).__init__(context,"lassen")
        self.PE = self.add_peak_primitive("PE",gen_pe)

        #Map constants to Full PE (for now)
        self.__const16_rr()
        #self.const1_rr()

        #Map float add/mul
        context.load_library("float")
        self.__float_add_rr()
        self.__float_mul_rr()

        #Bitwise values
        self.__bitwise()

        #Map IO to IO tiles
        self.add_io_and_rewrite("io1", 1, "io2f_1", "f2io_1")
        self.add_io_and_rewrite("io16", 16, "io2f_16", "f2io_16")

    def __const16_rr(self):

        const16 = self.context.get_namespace("coreir").generators['const'](width=16)
        def instr_lambda(inst):
            cval = inst.config["value"].value
            return asm.const(cval)

        #Adds a simple "1 to 1" rewrite rule
        self.add_rewrite_rule(mm.Peak1to1(
            const16,
            self.PE,
            instr_lambda,
            dict(out="alu_res")
        ))

    def __const1_rr(self):
        raise NotImplemented()

    def __float_add_rr(self):
        bfloat_add = self.context.get_namespace("float").generators['add'](exp_bits=8,frac_bits=7)

        self.add_rewrite_rule(mm.Peak1to1(
            bfloat_add, #Coreir module
            self.PE, #coreir pe
            asm.fp_add(), #Instruction for PE
            dict(in0='data0',in1='data1',out="alu_res") #Port Mapping
        ))

    def __float_mul_rr(self):
        bfloat_mul = self.context.get_namespace("float").generators['mul'](exp_bits=8,frac_bits=7)

        self.add_rewrite_rule(mm.Peak1to1(
            bfloat_mul, #Coreir module
            self.PE, #coreir pe
            asm.fp_mult(), #Instruction for PE
            dict(in0='data0',in1='data1',out="alu_res") #Port Mapping
        ))


    #This should convert all the bitwise operators into LUTS
    def __bitwise(self):
        #Magic numbers 
        B0 = BitVector[8](170)
        B1 = BitVector[8](12*17)
        B2 = BitVector[8](15*16)

        lut_table = {
            "not" : ~B0,
            "and" : B0&B1,
            "or" : B0|B1,
            "xor" : B0^B1,
            "mux" : (B2&B1)|((~B2)&B0)
        }

        #Do the binary
        for op in ("and","or","xor"):
            cop = self.context.get_namespace("corebit").modules[op]
            self.add_rewrite_rule(mm.Peak1to1(
                cop,
                self.PE,
                asm.inst(ALU.Add,lut=lut_table[op],cond=Cond.LUT),
                dict(in0='bit0',in1='bit1',out='res_p')
            ))

        #unary:
        cop = self.context.get_namespace("corebit").modules["not"]
        self.add_rewrite_rule(mm.Peak1to1(
            cop,
            self.PE,
            asm.inst(ALU.Add,lut=lut_table[op],cond=Cond.LUT),
            {"in":'bit0',"out":'res_p'}
        ))

        #ternary:
        cop = self.context.get_namespace("corebit").modules["mux"]
        self.add_rewrite_rule(mm.Peak1to1(
            cop,
            self.PE,
            asm.inst(ALU.Add,lut=lut_table[op],cond=Cond.LUT),
            dict(in0='bit0',in1='bit1',sel='bit2',out='res_p')
        ))




