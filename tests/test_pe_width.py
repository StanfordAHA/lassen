"""The width-parameterized PE (gen_PE_fc) and its widened rewrite rules.

A lake spec with data_width W builds the CGRA at W bits, and garnet's PE is
gen_PE_fc(W): the integer PE at W bits with the 16-bit instruction layout and no
FP units. At 16 it must stay the stock PE_fc.
"""
import importlib
import json
import random
from pathlib import Path

import pytest
from hwtypes import Bit, BitVector
from peak.assembler import Assembler

from lassen import PE_fc, Inst_fc, gen_PE_fc, gen_Inst_fc
from lassen.alu import ALU_fc, ALU_t, Signed_t, gen_ALU_fc

WIDTHS = (8, 32, 64)
RULES = Path(__file__).resolve().parent.parent / "lassen"


def test_16_bits_is_the_stock_pe():
    assert gen_PE_fc(16) is PE_fc
    assert gen_Inst_fc(16) is Inst_fc
    assert gen_ALU_fc(16) is ALU_fc


@pytest.mark.parametrize("width", WIDTHS)
def test_generators_are_cached(width):
    # MetaMapper and garnet compare PE families by identity
    assert gen_PE_fc(width) is gen_PE_fc(width)
    assert gen_Inst_fc(width) is gen_Inst_fc(width)


@pytest.mark.parametrize("width", (8, 16, 32, 64))
def test_instruction_width(width):
    # Same fields at every width; only the three data constants are `width` bits
    assert Assembler(gen_Inst_fc(width).Py).width == 36 + 3 * width


def _sx(v, w):
    v &= (1 << w) - 1
    return v - (1 << w) if v >> (w - 1) else v


def _alu_ref(op, signed, a, b, c, d, w):
    m = (1 << w) - 1
    sa, sb, sc = (_sx(a, w), _sx(b, w), _sx(c, w)) if signed else (a, b, c)
    mul = (sa * sb) & ((1 << 2 * w) - 1)
    if op == ALU_t.Adc:
        return (a + b + d) & m
    if op == ALU_t.Sbc:
        return (a + (~b & m) + d) & m
    if op == ALU_t.Mult0:
        return mul & m
    if op == ALU_t.Mult1:
        return (mul >> (w // 2)) & m
    if op == ALU_t.Mult2:
        return (mul >> w) & m
    if op == ALU_t.And:
        return a & b
    if op == ALU_t.SHL:
        return (a << b) & m if b < w else 0
    if op == ALU_t.SHR:
        if c >= w:
            return m if (signed and sa < 0) else 0
        return (sa >> c) & m if signed else a >> c
    if op == ALU_t.MULADD:
        return (mul + c) & m
    if op == ALU_t.CROP:
        return max(min(sa, sb), sc) & m
    raise KeyError(op)


ALU_OPS = (ALU_t.Adc, ALU_t.Sbc, ALU_t.Mult0, ALU_t.Mult1, ALU_t.Mult2, ALU_t.And,
           ALU_t.SHL, ALU_t.SHR, ALU_t.MULADD, ALU_t.CROP)


@pytest.mark.parametrize("width", (8, 16, 32, 64))
@pytest.mark.parametrize("op", ALU_OPS, ids=lambda op: op.name)
@pytest.mark.parametrize("signed", (False, True), ids=("u", "s"))
def test_alu_matches_reference(width, op, signed):
    rng = random.Random(f"{width}-{op.name}-{signed}")
    alu = gen_ALU_fc(width).Py()
    sign = Signed_t.signed if signed else Signed_t.unsigned
    for _ in range(64):
        a, b, c = (rng.getrandbits(width) for _ in range(3))
        if op == ALU_t.SHL:
            b = rng.randrange(width + 2)
        if op == ALU_t.SHR:
            c = rng.randrange(width + 2)
        d = rng.getrandbits(1) if op in (ALU_t.Adc, ALU_t.Sbc) else 0
        res = alu(op, sign, BitVector[width](a), BitVector[width](b), BitVector[width](c), Bit(d))[0]
        assert int(res) == _alu_ref(op, signed, a, b, c, d, width), (hex(a), hex(b), hex(c), d)


def _integer_rules():
    """The 16-bit rules scripts/widen_rewrite_rules.py widens: no FP / bf16 ones."""
    src = RULES / "rewrite_rules"
    names = []
    for py in sorted(src.glob("*.py")):
        js = py.with_suffix(".json")
        if py.stem == "__init__" or not js.exists():
            continue
        text, rule = py.read_text(), js.read_text()
        if any(s in text for s in ("BFloat", "float", "Float")) or '"fpu"' in rule or '"fp_custom"' in rule:
            continue
        names.append(py.stem)
    return names


@pytest.mark.parametrize("width", WIDTHS)
def test_every_integer_rule_is_widened(width):
    have = sorted(p.stem for p in (RULES / f"rewrite_rules_w{width}").glob("*.json"))
    assert have == _integer_rules()
    assert not list((RULES / f"rewrite_rules_w{width}").glob("*.failed"))


@pytest.mark.parametrize("width", WIDTHS)
def test_widened_rules_verify_against_the_pe(width):
    # Each rule's binding is SMT-checked against gen_PE_fc(width): the rules MetaMapper
    # maps with at that width are correct for that PE.
    from peak.mapper import read_serialized_bindings
    pe = gen_PE_fc(width)
    for name in _integer_rules():
        mod = importlib.import_module(f"lassen.rewrite_rules_w{width}.{name}")
        with open(RULES / f"rewrite_rules_w{width}" / f"{name}.json") as f:
            rr = read_serialized_bindings(json.load(f), getattr(mod, name + "_fc"), pe)
        assert rr.verify() is None, f"{name} at {width} bits"
