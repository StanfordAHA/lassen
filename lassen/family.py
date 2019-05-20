import magma as m
from collections import namedtuple
from hwtypes import BitVector, SIntVector, TypeFamily
import hwtypes.adt
from hwtypes import SMTBitVector


ExtendedTypeFamily = namedtuple('ExtendedTypeFamily', ['Bit', 'BitVector',
                                                       'Unsigned', 'Signed',
                                                       'Product', 'Enum',
                                                       'overflow', 'BFloat16'])


def gen_pe_type_family(family):
    if family is BitVector.get_family() or family is SMTBitVector.get_family():
        from hwtypes import overflow, FPVector, RoundingMode
        BFloat16 = FPVector[7,8,RoundingMode.RNE,False]
        family = ExtendedTypeFamily(*family, hwtypes.adt.Product, hwtypes.adt.Enum,
                                    overflow, BFloat16)
    elif family is m.get_family():
        from mantle.common.operator import overflow
        family = ExtendedTypeFamily(*family, m.Product, m.Enum, overflow, m.BFloat[16])
    else:
        raise NotImplementedError(family)
    return family
