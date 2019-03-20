from lassen.asm import add, sub, and_, or_, xor
from lassen.sim import gen_pe, gen_pe_type_family
from lassen.mode import gen_mode_type
from lassen.isa import DATAWIDTH, gen_inst_type
import magma as m
import pytest
from hwtypes import BitVector
import fault
from peak.auto_assembler import generate_assembler

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

@pytest.mark.parametrize('op', [add, and_, or_, xor])
@pytest.mark.parametrize('mode', [Mode.BYPASS, Mode.DELAY])
@pytest.mark.parametrize('use_assembler', [False, True])
def test_rtl(op, mode, use_assembler):
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
    tester.compile_and_run(target="verilator",
                           directory="tests/build/",
                           flags=['-Wno-UNUSED', '--trace'],
                           skip_compile=True)
