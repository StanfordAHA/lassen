from peak import Peak, gen_register, family_closure
from hwtypes.adt_util import rebind_type
from functools import lru_cache
from hwtypes.adt import Enum
"""
Field for specifying register modes
"""
class Mode_t(Enum):
    CONST = 0   # Register returns constant in constant field
    BYPASS = 2  # Register is bypassed and input value is returned
    DELAY = 3   # Register written with input value, previous value returned


def gen_bit_mode(init):
    return gen_register_mode(None, init)

@lru_cache(None)
def gen_register_mode(width, init):
    @family_closure
    def RegisterMode_fc(family):
        if width is None:
            T = family.Bit
        else:
            T = family.BitVector[width]

        Reg = family.gen_register(T, init)
        Bit = family.Bit

        @family.assemble(locals(), globals())
        class RegisterMode(Peak):
            def __init__(self):
                self.register: Reg = Reg()

            #Outputs <based on mode>, register_value
            def __call__(self, mode: Mode_t, const_: T, value: T,
                    clk_en: Bit, config_we : Bit, config_data : T) -> (T, T):
                if config_we:
                    data, en = config_data, Bit(1)
                elif mode == Mode_t.DELAY:
                    data, en = value, clk_en
                else:
                    data, en = value, Bit(0)

                reg_val = self.register(data, en)

                if mode == Mode_t.CONST:
                    return const_, reg_val
                elif mode == Mode_t.BYPASS:
                    return value, reg_val
                else: # mode == Mode_t.DELAY:
                    return reg_val, reg_val
        return RegisterMode
    return RegisterMode_fc

