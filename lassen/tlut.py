from lassen.utils import bfbin2float, float2bfbin
import math


class tlut:
    def div_lut(self, index):
        x = 1.0 + float(int(index)) / 128.0
        x_inv = 1.0 / x
        return int(float2bfbin(x_inv), 2)

    def ln_lut(self, index):
        x = 1.0 + float(int(index)) / 128.0
        return int(float2bfbin(math.log(x)), 2)

    def exp_lut(self, index):
        x = 0.0 + float(int(index)) / 128.0
        return int(float2bfbin((2**x)), 2)
