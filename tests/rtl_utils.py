import os

import shutil

import fault
from hwtypes import Bit, BitVector
import magma
from peak import wrap_with_disassembler
from peak.assembler import Assembler
from peak.family import PyFamily, MagmaFamily

from lassen import PE_fc, Inst_fc
from lassen.common import DATAWIDTH, BFloat16_fc


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))


Inst = Inst_fc(PyFamily())
Mode_t = Inst.rega

PE_bv = PE_fc(PyFamily())

BFloat16 = BFloat16_fc(PyFamily())
Data = BitVector[DATAWIDTH]

# create these variables in global space so that we can reuse them easily
inst_name = "inst"
inst_type = PE_bv.input_t.field_dict[inst_name]

_assembler = Assembler(inst_type)
assembler = _assembler.assemble
disassembler = _assembler.disassemble
width = _assembler.width
layout = _assembler.layout
PE_magma = PE_fc(MagmaFamily())
instr_magma_type = type(PE_magma.interface.ports[inst_name])
pe_circuit = wrap_with_disassembler(
    PE_magma, disassembler, width, HashableDict(layout), instr_magma_type
)
tester = fault.Tester(pe_circuit, clock=pe_circuit.CLK)
test_dir = "tests/build"

# Explicitly load `float_DW` lib so we get technology specific mapping with
# special code for BFloat rounding, for more info:
# * https://github.com/rdaly525/coreir/pull/753
# * https://github.com/StanfordAHA/lassen/issues/111
# We reset the context because tests/test_micro.py calls compile and pollutes
# the coreir context causing a "redefinition of module" error
magma.frontend.coreir_.ResetCoreIR()
magma.compile(
    f"{test_dir}/WrappedPE",
    pe_circuit,
    output="coreir-verilog",
    coreir_libs={"float_DW"},
    sv=True,
)

# check if we need to use ncsim + cw IP
cw_dir = "/cad/synopsys/dc_shell/J-2014.09-SP3/dw/sim_ver/"  # noqa
CAD_ENV = shutil.which("ncsim") and os.path.isdir(cw_dir)


def copy_file(src_filename, dst_filename, override=False):
    if not override and os.path.isfile(dst_filename):
        return
    shutil.copy(src_filename, dst_filename)


def rtl_tester(
    test_op,
    data0=None,
    data1=None,
    data2=None,
    bit0=None,
    bit1=None,
    bit2=None,
    res=None,
    res_p=None,
    clk_en=1,
    delay=0,
    data0_delay_values=None,
    data1_delay_values=None,
    data2_delay_values=None,
):
    tester.clear()
    # Advance timestep past 0 for fp functional model (see rnd logic)
    tester.circuit.ASYNCRESET = 0
    tester.eval()
    tester.circuit.ASYNCRESET = 1
    tester.eval()
    tester.circuit.ASYNCRESET = 0
    tester.eval()
    if hasattr(test_op, "inst"):
        tester.circuit.inst = assembler(test_op.inst)
    else:
        tester.circuit.inst = assembler(test_op)
    tester.circuit.CLK = 0
    tester.circuit.clk_en = clk_en
    if data0 is not None:
        data0 = BitVector[16](data0)
        tester.circuit.data0 = data0
    if data1 is not None:
        data1 = BitVector[16](data1)
        tester.circuit.data1 = data1
    if data2 is not None:
        data2 = BitVector[16](data2)
        tester.circuit.data2 = data2
    if bit0 is not None:
        tester.circuit.bit0 = Bit(bit0)
    if bit1 is not None:
        tester.circuit.bit1 = Bit(bit1)
    if bit2 is not None:
        tester.circuit.bit2 = Bit(bit2)

    tester.eval()

    for i in range(delay):
        tester.step(2)
        if data0_delay_values is not None:
            tester.circuit.data0 = data0_delay_values[i]
        if data1_delay_values is not None:
            tester.circuit.data1 = data1_delay_values[i]
        if data2_delay_values is not None:
            tester.circuit.data2 = data2_delay_values[i]

    if res is not None:
        tester.circuit.O0.expect(res)
    if res_p is not None:
        tester.circuit.O1.expect(res_p)
    if CAD_ENV:
        # use ncsim
        libs = ["DW_fp_mult.v", "DW_fp_add.v", "DW_fp_addsub.v"]
        for filename in libs:
            copy_file(os.path.join(cw_dir, filename), os.path.join(test_dir, filename))
        tester.compile_and_run(
            target="system-verilog",
            simulator="ncsim",
            directory="tests/build/",
            include_verilog_libraries=libs,
            skip_compile=True,
            magma_opts={"sv": True},
        )
    else:
        libs = ["DW_fp_mult.v", "DW_fp_add.v"]
        for filename in libs:
            copy_file(os.path.join("stubs", filename), os.path.join(test_dir, filename))
        # detect if the PE circuit has been built
        skip_verilator = os.path.isfile(
            os.path.join(test_dir, "obj_dir", "VWrappedPE__ALL.a")
        )
        tester.compile_and_run(
            target="verilator",
            directory=test_dir,
            flags=["-Wno-UNUSED", "-Wno-PINNOCONNECT"],
            skip_compile=True,
            skip_verilator=skip_verilator,
            magma_opts={"sv": True},
        )
