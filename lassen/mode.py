from peak import Peak, gen_register
from functools import lru_cache
from hwtypes import Enum, Bit, BitVector


"""
Field for specifying register modes
"""
class Mode_t(Enum):
    CONST = 0   # Register returns constant in constant field
    BYPASS = 2  # Register is bypassed and input value is returned
    DELAY = 3   # Register written with input value, previous value returned

@lru_cache(None)
def gen_register_mode(T, init=None):
    if init is None:
        init = T(0)
    Reg = gen_register(T, init=init)

    class RegisterMode(Peak):
        def __init__(self):
            self.register: Reg = Reg()

        #Outputs <based on mode>, register_value
        def __call__(self, mode: Mode_t, const_: T, value: T,
                clk_en: Bit, config_we : Bit, config_data : T) -> (T,T):
            if config_we==Bit(1):
                reg_val = self.register(config_data,Bit(1))
            elif mode == Mode_t.DELAY:
                reg_val = self.register(value, clk_en)
            else:
                reg_val = self.register(value, Bit(0))

            if mode == Mode_t.CONST:
                return const_, reg_val
            elif mode == Mode_t.BYPASS:
                return value, reg_val
            elif mode == Mode_t.DELAY:
                return reg_val, reg_val

    return RegisterMode
