from hwtypes import BitVector, Bit

def gen_lut_type(family):
    # Types for LUT operations
    return family.BitVector[8]

_IDX_t = BitVector[3]

def gen_lut(family):
    LUT = gen_lut_type(family)
    # Implement a 3-bit LUT
    def lut( lut:LUT, bit0:Bit, bit1:Bit, bit2:Bit) -> Bit:
        i = _IDX_t([bit0, bit1, bit2])
        i = i.zext(5)
        return ((lut >> i) & 1)[0]
    return lut
