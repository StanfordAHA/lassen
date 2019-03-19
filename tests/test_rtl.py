from lassen.asm import add, sub, and_, or_, xor
from lassen.sim import gen_pe, gen_pe_type_family
from lassen.mode import gen_mode_type
import magma as m
import pytest
from hwtypes import BitVector


Mode = gen_mode_type(gen_pe_type_family(BitVector.get_family()))


@pytest.mark.skip("WIP")
@pytest.mark.parametrize('op', [add, and_, or_, xor])
@pytest.mark.parametrize('mode', [Mode.BYPASS, Mode.DELAY])
def test_rtl(op, mode):
    pe_functional_model = gen_pe(BitVector.get_family())()
    pe_magma = gen_pe(m.get_family())
    tester = fault.Tester(pe_magma, clock=PE.CLK)

    inst = op(ra_mode=mode, rb_mode=mode)
    tester.circuit.inst = inst.value
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

    m.compile(f"build/pe_magma", pe_magma, output="coreir-verilog")
    tester.compile_and_run(target="verilator",
                           directory="tests/test_syntax/build/",
                           flags=['-Wno-UNUSED', '--trace'],
                           skip_compile=True)

