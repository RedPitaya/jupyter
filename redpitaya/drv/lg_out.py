from ctypes import *
import numpy as np

class lg_out (object):
    class _regset_t (Structure):
        _fields_ = [('cfg_oen', c_uint32),  # output enable
                    ('cfg_msk', c_uint32),  # bit mask
                    ('cfg_val', c_uint32),  # bit value
                    ('cfg_pol', c_uint32)]  # polarity inversion

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        print (
            "cfg_oen = 0x{reg:08x} = {reg:10d}  # output enable     \n".format(reg=self.regset.out.cfg_oen)+
            "cfg_msk = 0x{reg:08x} = {reg:10d}  # bit mask          \n".format(reg=self.regset.out.cfg_msk)+
            "cfg_val = 0x{reg:08x} = {reg:10d}  # bit value         \n".format(reg=self.regset.out.cfg_val)+
            "cfg_pol = 0x{reg:08x} = {reg:10d}  # polarity inversion\n".format(reg=self.regset.out.cfg_pol)
        )

    @property
    def enable (self) -> int:
        """Output enable."""
        return (self.regset.out.cfg_oen)

    @enable.setter
    def enable (self, value: int):
        self.regset.out.cfg_oen = value

    @property
    def mask (self) -> int:
        """Output mask."""
        return (self.regset.out.cfg_msk)

    @mask.setter
    def mask (self, value: int):
        self.regset.out.cfg_sum = value

    @property
    def value (self) -> int:
        """Output value."""
        return (self.regset.out.cfg_val)

    @value.setter
    def value (self, value: int):
        self.regset.out.cfg_val = value

    @property
    def polarity (self) -> int:
        """Output polarity inversion."""
        return (self.regset.out.cfg_pol)

    @polarity.setter
    def polarity (self, value: int):
        self.regset.out.cfg_pol = value