"""lassen Cond (the PE's 1-bit predicate) against the condition-code table.

Cond computes every condition at once and selects one with an AND-OR tree
(a 20-way if/elif synthesized into a serial chain of 19 muxes); this checks it
against that table for every named code and every input."""
import itertools

from peak import family

from lassen.cond import Cond_fc, Cond_t


def reference(code, alu, lut, Z, N, C, V):
    nv = N == V
    return {
        0: Z, 1: not Z, 2: C, 3: not C, 4: N, 5: not N, 6: V, 7: not V,
        8: C and not Z, 9: (not C) or Z, 10: nv, 11: not nv,
        12: (not Z) and nv, 13: Z or not nv, 14: lut, 15: alu,
        16: (not N) or Z, 17: (not N) and (not Z), 18: N or Z,
        19: N and not Z,
    }[code]


def test_cond_matches_the_condition_table():
    Bit = family.PyFamily().Bit
    cond = Cond_fc.Py()
    codes = {}
    for name in dir(Cond_t):
        v = getattr(Cond_t, name)
        if isinstance(v, Cond_t):
            codes[int(v._value_)] = v
    assert sorted(codes) == list(range(20))
    for value, code in codes.items():
        for bits in itertools.product([False, True], repeat=6):
            got = cond(code, *[Bit(b) for b in bits])
            assert bool(got) == bool(reference(value, *bits)), (code, bits)
