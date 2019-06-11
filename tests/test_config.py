import os
from collections import namedtuple
import lassen.asm as asm
from lassen.sim import gen_pe, gen_pe_type_family
from lassen.mode import gen_mode_type
from lassen.isa import *
from hwtypes import SIntVector, UIntVector, BitVector, Bit, FPVector, RoundingMode
import pytest
import magma
import peak
import fault
from itertools import product
import os
import random
import shutil
from peak.auto_assembler import generate_assembler
import random

class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))

Bit = Bit
Data = BitVector[DATAWIDTH]
Data32 = BitVector[32]
Data8 = BitVector[32]
BFloat16 = FPVector[8,7,RoundingMode.RNE,False]

pe_ = gen_pe(BitVector.get_family())
pe = pe_()
sim_family = gen_pe_type_family(BitVector.get_family())
Mode = gen_mode_type(sim_family)

# create these variables in global space so that we can reuse them easily
instr_name, inst_type = pe.__call__._peak_isa_
assembler, disassembler, width, layout = \
            generate_assembler(inst_type)
#pe_magma = gen_pe(magma.get_family(), use_assembler=True)
#instr_magma_type = type(pe_magma.interface.ports[instr_name])
#pe_circuit = peak.wrap_with_disassembler(pe_magma, disassembler, width,
#                                         HashableDict(layout),
#                                         instr_magma_type)
#tester = fault.Tester(pe_circuit, clock=pe_circuit.CLK)
#test_dir = "tests/build"
#magma.compile(f"{test_dir}/WrappedPE", pe_circuit, output="coreir-verilog")
#
## check if we need to use ncsim + cw IP
#cw_dir = "/cad/cadence/GENUS17.21.000.lnx86/share/synth/lib/chipware/sim/verilog/CW/"   # noqa
#CAD_ENV = shutil.which("ncsim") and os.path.isdir(cw_dir)
#
#
#def copy_file(src_filename, dst_filename, override=False):
#    if not override and os.path.isfile(dst_filename):
#        return
#    shutil.copy(src_filename, dst_filename)
#
#
#def rtl_tester(test_op, data0=None, data1=None, bit0=None, bit1=None, bit2=None,
#               res=None, res_p=None, clk_en=1, delay=0,
#               data0_delay_values=None, data1_delay_values=None):
#    tester.clear()
#    if hasattr(test_op, "inst"):
#        tester.circuit.inst = assembler(test_op.inst)
#    else:
#        tester.circuit.inst = assembler(test_op)
#    tester.circuit.CLK = 0
#    tester.circuit.clk_en = clk_en
#    if data0 is not None:
#        data0 = BitVector[16](data0)
#        tester.circuit.data0 = data0
#    if data1 is not None:
#        data1 = BitVector[16](data1)
#        tester.circuit.data1 = data1
#    if bit0 is not None:
#        tester.circuit.bit0 = Bit(bit0)
#    if bit1 is not None:
#        tester.circuit.bit1 = Bit(bit1)
#    if bit2 is not None:
#        tester.circuit.bit2 = Bit(bit2)
#    tester.eval()
#
#    for i in range(delay):
#        tester.step(2)
#        if data0_delay_values is not None:
#            tester.circuit.data0 = data0_delay_values[i]
#        if data1_delay_values is not None:
#            tester.circuit.data1 = data1_delay_values[i]
#
#    if res is not None:
#        tester.circuit.O0.expect(res)
#    if res_p is not None:
#        tester.circuit.O1.expect(res_p)
#    if CAD_ENV:
#        # use ncsim
#        libs = ["CW_fp_mult.v", "CW_fp_add.v"]
#        for filename in libs:
#            copy_file(os.path.join(cw_dir, filename),
#                      os.path.join(test_dir, filename))
#        tester.compile_and_run(target="system-verilog", simulator="ncsim",
#                               directory="tests/build/",
#                               include_verilog_libraries=libs,
#                               skip_compile=True)
#    else:
#        libs = ["CW_fp_mult.v", "CW_fp_add.v"]
#        for filename in libs:
#            copy_file(os.path.join("stubs", filename),
#                      os.path.join(test_dir, filename))
#        # detect if the PE circuit has been built
#        skip_verilator = os.path.isfile(os.path.join(test_dir, "obj_dir",
#                                                     "VWrappedPE__ALL.a"))
#        tester.compile_and_run(target="verilator",
#                               directory=test_dir,
#                               flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
#                               skip_compile=True,
#                               skip_verilator=skip_verilator)
#

NTESTS = 16

#@pytest.mark.parametrize("args", [
#    (UIntVector.random(DATAWIDTH), UIntVector.random(DATAWIDTH))
#        for _ in range(NTESTS) ] )

def write_data01(pe,data0 : Data, data1 : Data):
    instr = asm.add()
    config_addr = Data8(DATA01_ADDR)
    config_data = BitVector.concat(data0,data1)
    config_en = Bit(1)
    return pe(instr,data0=Data(0),config_addr=config_addr,config_data=config_data,config_en=config_en)

def read_data0(pe):
    instr = asm.add()
    config_addr = Data8(DATA01_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[DATA0_START:DATA0_START+DATA0_WIDTH]

def read_data1(pe):
    instr = asm.add()
    config_addr = Data8(DATA01_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[DATA1_START:DATA1_START+DATA1_WIDTH]

@pytest.mark.parametrize("args",[
    (BitVector.random(DATAWIDTH), BitVector.random(DATAWIDTH))
        for _ in range(NTESTS)
])
def test_config_data01(args):
    write_data01(pe,args[0],args[1])
    assert args[0] == read_data0(pe)
    assert args[1] == read_data1(pe)

def write_bit012(pe,bit0 : Bit, bit1 : Bit, bit2 : Bit):
    instr = asm.add()
    BV1 = BitVector[1]
    config_addr = Data8(BIT012_ADDR)
    config_data = BitVector.concat(BitVector.concat(BitVector.concat(BV1(bit0),BV1(bit1)),BV1(bit2)),BitVector[29](0))
    config_en = Bit(1)
    return pe(instr,data0=Data(0),config_addr=config_addr,config_data=config_data,config_en=config_en)

def read_bit0(pe):
    instr = asm.add()
    config_addr = Data8(BIT012_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[BIT0_START]

def read_bit1(pe):
    instr = asm.add()
    config_addr = Data8(BIT012_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[BIT1_START]

def read_bit2(pe):
    instr = asm.add()
    config_addr = Data8(BIT012_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[BIT2_START]

@pytest.mark.parametrize("args",[
    (Bit(random.randint(0,1)),
     Bit(random.randint(0,1)),
     Bit(random.randint(0,1)))
        for _ in range(NTESTS)
])
def test_config_bit012(args):
    write_bit012(pe,args[0],args[1],args[2])
    assert args[0] == read_bit0(pe)
    assert args[1] == read_bit1(pe)
    assert args[2] == read_bit2(pe)






