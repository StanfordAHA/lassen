from hwtypes import BitVector, Bit
import tempfile
import os
import shutil

# check if we need to use ncsim + cw IP
cw_dir = "/cad/synopsys/dc_shell/J-2014.09-SP3/dw/sim_ver/"   # noqa
CAD_ENV = shutil.which("ncsim") and os.path.isdir(cw_dir)

base_compile_dir = "tests/build"


def copy_file(src_filename, dst_filename, override=False):
    if not override and os.path.isfile(dst_filename):
        return
    shutil.copy(src_filename, dst_filename)


def precompile_tester(tester):
    # run once to compile verilator/ncsim objects
    if CAD_ENV:
        libs = ["DW_fp_mult.v", "DW_fp_add.v", "DW_fp_addsub.v"]
        for filename in libs:
            copy_file(os.path.join(cw_dir, filename),
                      os.path.join(base_compile_dir, filename))
        tester.compile_and_run(target="system-verilog", simulator="ncsim",
                               directory=base_compile_dir,
                               include_verilog_libraries=libs,
                               skip_compile=True)
    else:
        tester.compile_and_run(target="verilator",
                               directory=base_compile_dir,
                               flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
                               skip_compile=True)


def rtl_tester(tester, assembler, test_op, data0=None, data1=None, bit0=None,
               bit1=None, bit2=None, res=None, res_p=None, clk_en=1, delay=0,
               data0_delay_values=None, data1_delay_values=None):
    tester.clear()
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
    if bit0 is not None:
        tester.circuit.bit0 = Bit(bit0)
    if bit1 is not None:
        tester.circuit.bit1 = Bit(bit1)
    if bit2 is not None:
        tester.circuit.bit2 = Bit(bit2)
    # make sure config_en is off
    tester.circuit.config_en = Bit(0)
    tester.eval()

    for i in range(delay):
        tester.step(2)
        if data0_delay_values is not None:
            tester.circuit.data0 = data0_delay_values[i]
        if data1_delay_values is not None:
            tester.circuit.data1 = data1_delay_values[i]

    if res is not None:
        tester.circuit.O0.expect(res)
    if res_p is not None:
        tester.circuit.O1.expect(res_p)
    test_dir = tempfile.mkdtemp()
    try:
        shutil.copy(f"{base_compile_dir}/WrappedPE.v",
                    f"{test_dir}/WrappedPE.v")
        if CAD_ENV:
            # use ncsim
            libs = ["DW_fp_mult.v", "DW_fp_add.v", "DW_fp_addsub.v"]
            for filename in libs:
                copy_file(os.path.join(cw_dir, filename),
                          os.path.join(test_dir, filename))
            shutil.copytree(os.path.join(base_compile_dir, "INCA_LIBS"),
                            os.path.join(test_dir, "INCA_LIBS"))
            tester.compile_and_run(target="system-verilog", simulator="ncsim",
                                   directory=test_dir,
                                   include_verilog_libraries=libs,
                                   skip_compile=True)
        else:
            libs = ["DW_fp_mult.v", "DW_fp_add.v"]
            for filename in libs:
                copy_file(os.path.join("stubs", filename),
                          os.path.join(test_dir, filename))
            shutil.copytree(os.path.join(base_compile_dir, "obj_dir"),
                            os.path.join(test_dir, "obj_dir"))
            tester.compile_and_run(target="verilator",
                                   directory=test_dir,
                                   flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
                                   skip_compile=True,
                                   skip_verilator=True)
        shutil.rmtree(test_dir)
    except AssertionError as e:
        print("Test failed, see directory: {test_dir}")
        raise e
