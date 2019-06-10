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
        self._const16_rr()
        #self.const1_rr()

        #Map float add/mul
        context.load_library("float")
        self._float_binary_rr()
        self._float_cmp_rr()

        #Bitwise values
        self._bitwise()

        #Map IO to IO tiles
        self.add_io_and_rewrite("io1", 1, "io2f_1", "f2io_1")
        self.add_io_and_rewrite("io16", 16, "io2f_16", "f2io_16")

    def _const16_rr(self):

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

    def _float_binary_rr(self):
        for op in ['add','mul','sub']:
            coreir_op = self.context.get_namespace("float").generators[op](exp_bits=8,frac_bits=7)
            instr = getattr(asm,f"fp_{op}")()
            self.add_rewrite_rule(mm.Peak1to1(
                coreir_op, #Coreir module
                self.PE, #coreir pe
                instr, #Instruction for PE
                dict(in0='data0',in1='data1',out="alu_res") #Port Mapping
            ))

    def _float_cmp_rr(self):
        for op in ['le','lt','ge','gt','eq','neq']:
            coreir_op = self.context.get_namespace("float").generators[op](exp_bits=8,frac_bits=7)
            instr = getattr(asm,f"fp_{op}")()
            self.add_rewrite_rule(mm.Peak1to1(
                coreir_op, #Coreir module
                self.PE, #coreir pe
                instr, #Instruction for PE
                dict(in0='data0',in1='data1',out="res_p") #Port Mapping
            ))

    #This should convert all the bitwise operators into LUTS
    def _bitwise(self):

        #Do the binary
        for op in ("and","or","xor"):
            cop = self.context.get_namespace("corebit").modules[op]
            self.add_rewrite_rule(mm.Peak1to1(
                cop,
                self.PE,
                getattr(asm,f"lut_{op}")(),
                dict(in0='bit1',in1='bit2',out='res_p')
            ))

        #unary:
        cop = self.context.get_namespace("corebit").modules["not"]
        self.add_rewrite_rule(mm.Peak1to1(
            cop,
            self.PE,
            asm.lut_not(),
            {"in":'bit1',"out":'res_p'}
        ))

        #ternary:
        cop = self.context.get_namespace("corebit").modules["mux"]
        self.add_rewrite_rule(mm.Peak1to1(
            cop,
            self.PE,
            asm.lut_mux(),
            dict(in0='bit0',in1='bit1',sel='bit2',out='res_p')
        ))




