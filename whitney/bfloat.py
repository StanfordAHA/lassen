from bit_vector import BitVector
import struct
import numpy as np

def _bv_to_bfloat(a: BitVector):
    assert (a.num_bits == 16)
    # Turn in to equivalent float32
    a_ext = BitVector.concat(a, BitVector(0, 16))
    # Change to 4 raw bytes
    raw_data = struct.pack('<I', a_ext.as_uint())
    # Re-interpret raw-bytes as np.float32
    fp = np.frombuffer(raw_data, dtype = np.float32)
    return fp
   
def _bfloat_to_bv(fp: np.float32):
    # Change np.float32 to 4 raw bytes
    raw_data = struct.pack('<f', fp)
    # Re-interpret 4 raw bytes as 2 unsigned ints
    # Convert float32 to bfloat16 by taking the upper 
    # 2 bytes (chop off 16 fraction bits)
    bv_value = struct.unpack('<HH', raw_data)[1]
    # Create BitVector from value
    bv = BitVector(bv_value, 16)
    return bv

class BFloat16(BitVector):

    def bfloat_add(self: BitVector, other: BitVector):
        a = _bv_to_bfloat(self)
        b = _bv_to_bfloat(other)
        return _bfloat_to_bv(a + b)
    
    def bfloat_sub(self: BitVector, other: BitVector):
        a = _bv_to_bfloat(self)
        b = _bv_to_bfloat(other)
        return _bfloat_to_bv(a - b)
    
    def bfloat_mul(self: BitVector, other: BitVector):
        a = _bv_to_bfloat(self)
        b = _bv_to_bfloat(other)
        return _bfloat_to_bv(a * b)

    def bfloat_neg(self: BitVector):
        # Just flip the sign bit
        res = BitVector(self)
        res[-1] = not res[-1]
        return res

    __add__ = bfloat_add
    __sub__ = bfloat_sub
    __mul__ = bfloat_mul
    __neg__ = bfloat_neg
