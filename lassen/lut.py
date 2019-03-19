import magma as m


def gen_lut_type(family):
    # Types for LUT operations
    return family.BitVector[8]


def gen_lut(family):
    LUT = gen_lut_type(family)
    _IDX_t = family.BitVector[3]
    Bit = family.Bit

    # Implement a 3-bit LUT
    def lut(lut: LUT, bit0: Bit, bit1: Bit, bit2: Bit) -> Bit:
        i = _IDX_t([bit0, bit1, bit2])
        i = i.zext(5)
        return ((lut >> i) & 1)[0]
    if family.Bit is m.Bit:
        lut = m.circuit.combinational(lut)
    return lut
