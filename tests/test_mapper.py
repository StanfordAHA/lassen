from lassen.alu import ALU_fc
from peak import Peak, family_closure
from peak.mapper import ArchMapper
from peak.mapper.utils import pretty_print_binding


@family_closure
def Add_fc(family):
    Data = family.BitVector[16]

    @family.assemble(locals(), globals())
    class Add(Peak):
        def __call__(self, a: Data, b: Data) -> Data:
            return a >> b

    return Add


def test_add():
    arch_fc = ALU_fc
    ir_fc = Add_fc
    arch_mapper = ArchMapper(arch_fc)
    ir_mapper = arch_mapper.process_ir_instruction(ir_fc)
    assert ir_mapper.formula is not None
    rr = ir_mapper.solve("z3")
    assert rr is not None
