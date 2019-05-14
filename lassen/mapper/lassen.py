
from lassen.sim import gen_pe
import lassen.asm as asm
from hwtypes import BitVector
import coreir
import metamapper as mm


class LassenMapper(mm.PeakMapper):
    def __init__(self,context : coreir.context):
        super(LassenMapper,self).__init__(context,"lassen")
        self.PE = self.add_peak_primitive("PE",gen_pe)

        #Map constants to Full PE (for now)
        self.const16_rr()
        #self.const1_rr()

        #Map float add/mul
        context.load_library("float")
        self.float_add_rr()
        self.float_mul_rr()

        #Map IO to IO tiles
        self.add_io_and_rewrite("io1", 1, "io2f_1", "f2io_1")
        self.add_io_and_rewrite("io16", 16, "io2f_16", "f2io_16")

    def const16_rr(self):

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

    def const1_rr(self):
        raise NotImplemented()

    def float_add_rr(self):
        bfloat_add = self.context.get_namespace("float").generators['add'](exp_bits=8,frac_bits=7)

        self.add_rewrite_rule(mm.Peak1to1(
            bfloat_add, #Coreir module
            self.PE, #coreir pe
            asm.fp_add(), #Instruction for PE
            dict(in0='data0',in1='data1',out="alu_res") #Port Mapping
        ))

    def float_mul_rr(self):
        bfloat_mul = self.context.get_namespace("float").generators['mul'](exp_bits=8,frac_bits=7)

        self.add_rewrite_rule(mm.Peak1to1(
            bfloat_mul, #Coreir module
            self.PE, #coreir pe
            asm.fp_mult(), #Instruction for PE
            dict(in0='data0',in1='data1',out="alu_res") #Port Mapping
        ))
