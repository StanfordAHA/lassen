from peak import Peak, gen_register, family_closure, update_peak, Enum_fc
from hwtypes.adt_util import rebind_type
from hwtypes import Enum
from functools import lru_cache
"""
Field for specifying register modes
"""
@lru_cache(None)
def Mode_t_fc(family):
    Enum = Enum_fc(family)
    class Mode_t(Enum):
        CONST = 0   # Register returns constant in constant field
        BYPASS = 2  # Register is bypassed and input value is returned
        DELAY = 3   # Register written with input value, previous value returned
    return Mode_t

def gen_register_mode(T, init=0):
    @family_closure
    def RegisterMode_fc(family):
        T_f = rebind_type(T, family)
        Reg = gen_register(T_f, init)(family)
        Bit = family.Bit
        Mode_t = Mode_t_fc(family)
        class RegisterMode(Peak):
            def __init__(self):
                self.register: Reg = Reg()

            #Outputs <based on mode>, register_value
            def __call__(self, mode: Mode_t, const_: T_f, value: T_f,
                    clk_en: Bit, config_we : Bit, config_data : T_f) -> (T_f,T_f):
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
                else: # mode == Mode_t.DELAY:
                    return reg_val, reg_val
        return update_peak(RegisterMode, family)

    return RegisterMode_fc
