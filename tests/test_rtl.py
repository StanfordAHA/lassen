from lassen.asm import add, sub, and_, or_, xor, fp_mult, fp_add, faddiexp, \
    fsubexp, fcnvexp2f, fgetfint, fgetffrac, smax
from lassen.sim import gen_pe, gen_pe_type_family
from lassen.mode import gen_mode_type
from lassen.isa import DATAWIDTH, gen_inst_type
from lassen.lut import gen_lut
import magma as m
import pytest
from hwtypes import BitVector
import fault
from peak.auto_assembler import generate_assembler
import os


Mode = gen_mode_type(gen_pe_type_family(BitVector.get_family()))


def wrap_with_disassembler(PE, disassembler, width, layout, inst_type):
    WrappedIO = []
    for key, value in PE.interface.ports.items():
        WrappedIO.append(key)
        if type(value) == m.Out(inst_type):
            WrappedIO.append(m.In(m.Bits[width]))
        else:
            WrappedIO.append(m.Flip(type(value)))

    def wire_inst_fields(wrapper_inst, pe_inst, layout):
        if isinstance(wrapper_inst, m.Product):
            for key, value in layout.items():
                begin = value[0]
                end = value[1]
                wire_inst_fields(wrapper_inst[begin:end], getattr(pe_inst,
                                                                  key),
                                 value[2])
        else:
            for key, value in layout.items():
                begin = value[0]
                end = value[1]
                region = wrapper_inst[begin:end]
                field = getattr(pe_inst, key)
                if isinstance(type(field), m._BitKind):
                    region = m.bit(region)
                m.wire(region, field)

    class WrappedPE(m.Circuit):
        IO = WrappedIO
        @classmethod
        def definition(io):
            pe = PE()
            for key, value in PE.interface.ports.items():
                if type(value) == m.Out(inst_type):
                    wire_inst_fields(getattr(io, key), getattr(pe, key),
                                     layout)
                elif value.isoutput():
                    getattr(pe, key) <= getattr(io, key)
                else:
                    getattr(io, key) <= getattr(pe, key)
    return WrappedPE


@pytest.mark.parametrize('op', [smax, add, and_, or_, xor, fp_add, fp_mult, faddiexp,
                                fsubexp, fcnvexp2f, fgetfint, fgetffrac])
@pytest.mark.parametrize('mode', [Mode.BYPASS, Mode.DELAY])
@pytest.mark.parametrize('use_assembler', [False, True])
def test_rtl(op, mode, use_assembler):
    libs = [
        "/cad/cadence/GENUS17.21.000.lnx86/share/synth/lib/chipware/sim/verilog/CW/CW_fp_mult.v",
        "/cad/cadence/GENUS17.21.000.lnx86/share/synth/lib/chipware/sim/verilog/CW/CW_fp_add.v"
    ]
    CW_avail = all(os.path.isfile(file) for file in libs)
    if not CW_avail and op in {fp_add, fp_mult}:
        pytest.skip("Skipping fp op tests because CW primitives are not available")

    inst_type = gen_inst_type(gen_pe_type_family(BitVector.get_family()))
    inst = op(ra_mode=mode, rb_mode=mode)
    if use_assembler:
        assembler, disassembler, width, layout = \
            generate_assembler(inst_type)
    else:
        assembler = lambda x: x
    PE = gen_pe(m.get_family(), assembler=assembler)
    if use_assembler:
        PE = wrap_with_disassembler(PE, disassembler, width, layout,
                                    gen_inst_type(gen_pe_type_family(m.get_family())))

    pe_functional_model = gen_pe(BitVector.get_family())()
    tester = fault.Tester(PE, clock=PE.CLK)

    if not use_assembler:
        tester.circuit.inst = inst.value
    else:
        tester.circuit.inst = assembler(inst)
    tester.circuit.CLK = 0
    # Special case these inputs because they are known to work from test_pe
    if op == fp_add:
        data0, data1 = 0x801, 0x782
    elif op == fp_mult:
        data0, data1 = 0x4080, 0x4001
    elif op == faddiexp:
        data0, data1 = 0x7F8A, 0x0000
    elif op == fsubexp:
        data0, data1 = 0x7F8A, 0x0000
    elif op == fcnvexp2f:
        data0, data1 = 0x4005, 0x0000
    elif op == fgetfint:
        data0, data1 = 0x4020, 0x0000
    elif op == fgetffrac:
        data0, data1 = 0x4020, 0x0000
    elif op == smax:
        data0, data1 = 0xFFFF, 0x0002
    else:
        data0 = fault.random.random_bv(DATAWIDTH // 2)
        data1 = fault.random.random_bv(DATAWIDTH // 2)
    data0 = BitVector[16](data0)
    data1 = BitVector[16](data1)
    tester.circuit.data0 = data0
    tester.circuit.data1 = data1
    tester.eval()
    expected = pe_functional_model(inst, data0, data1)
    # TODO: Weird thing with conversions going on for fault signed values
    for i, value in enumerate(expected):
        getattr(tester.circuit, f"O{i}").expect(value)
    if mode == Mode.DELAY:
        tester.step(2)
        expected = pe_functional_model(inst, data0, data1)
        for i, value in enumerate(expected):
            getattr(tester.circuit, f"O{i}").expect(value)

    if not use_assembler:
        m.compile(f"tests/build/PE", PE, output="coreir-verilog")
    else:
        m.compile(f"tests/build/WrappedPE", PE, output="coreir-verilog")
    if CW_avail:
        tester.compile_and_run(target="system-verilog", simulator="ncsim",
                               directory="tests/build/",
                               include_verilog_libraries=libs,
                               skip_compile=True)
    else:
        tester.compile_and_run(target="verilator",
                               directory="tests/build/",
                               flags=['-Wno-UNUSED',  '-Wno-PINNOCONNECT'],
                               skip_compile=True)


def test_lut():
    lut_rtl = gen_lut(m.get_family()).circuit_definition
    lut_code = 0xEE
    tester = fault.Tester(lut_rtl)
    tester.circuit.lut = lut_code
    print("bit0, bit1, bit2,    O")
    for i in range(0, 8):
        bit0, bit1, bit2 = m.bitutils.int2seq(i, 3)
        tester.circuit.bit0 = bit0
        tester.circuit.bit1 = bit1
        tester.circuit.bit2 = bit2
        tester.eval()
        expected = (lut_code >> i) & 1
        tester.circuit.O.expect(expected)
        print(f"   {bit0}     {bit1}     {bit2}     {expected}")
    tester.compile_and_run(target="verilator", directory="tests/build",
                           flags=["-Wno-UNUSED"])
