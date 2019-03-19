import magma as m
from collections import namedtuple
from hwtypes import BitVector, SIntVector, TypeFamily
import peak.adt
# from .isa import gen_inst_type, gen_alu_type, gen_cond_type, gen_signed_type


ExtendedTypeFamily = namedtuple('ExtendedTypeFamily', ['Bit', 'BitVector',
                                                       'Unsigned', 'Signed',
                                                       'Product', 'Enum',
                                                       'overflow'])


# PETypeFamily = namedtuple('PETypeFamily', ['Bit', 'BitVector', 'UInt',
#                                            'SInt', 'Product', 'Enum', 'Inst',
#                                            'ALU', 'Cond', 'Signed'])


def gen_pe_type_family(family):
    if family is BitVector.get_family():
        from hwtypes import overflow
        family = ExtendedTypeFamily(*family, peak.adt.Product, peak.adt.Enum, overflow)
        # family = PETypeFamily(*family, gen_inst_type(family),
        #                       gen_alu_type(family), gen_cond_type(family),
        #                       gen_signed_type(family))
    elif family is m.get_family():
        from mantle.common.operator import overflow
        family = ExtendedTypeFamily(*family, m.Product, m.Enum, overflow)
        # family = PETypeFamily(*family, gen_inst_type(family),
        #                       gen_alu_type(family), gen_cond_type(family),
        #                       gen_signed_type(family))
    else:
        raise NotImplementedError(family)
    return family
