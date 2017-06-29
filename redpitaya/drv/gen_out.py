from ctypes import *
import numpy as np

class gen_out(object):
    # linear addition multiplication register width
    DWM = 14  #: data width - linear gain multiplier
    DWS = 14  #: data width - linear offset summand
    # fixed point range
    _DWMr = (1 << (DWM-2))
    _DWSr = (1 << (DWS-1)) - 1

    class _regset_t (Structure):
        _fields_ = [('cfg_mul',  c_int32),  # multiplier (amplitude)
                    ('cfg_sum',  c_int32),  # adder (offset)
                    ('cfg_ena', c_uint32)]  # output enable

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.out.cfg_mul = int(1 * self._DWMr)
        self.regset.out.cfg_sum = 0
        self.regset.out.cfg_ena = 0

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        print (
            "cfg_mul = 0x{reg:08x} = {reg:10d}  # multiplier (amplitude)\n".format(reg=self.regset.out.cfg_mul)+
            "cfg_sum = 0x{reg:08x} = {reg:10d}  # adder (offset)        \n".format(reg=self.regset.out.cfg_sum)+
            "cfg_ena = 0x{reg:08x} = {reg:10d}  # output enable         \n".format(reg=self.regset.out.cfg_ena)
        )

    @property
    def amplitude (self) -> float:
        """Output amplitude in range [-1,1] vols."""
        return (self.regset.out.cfg_mul / self._DWMr)

    @amplitude.setter
    def amplitude (self, value: float):
        if (-1.0 <= value <= 1.0):
            self.regset.out.cfg_mul = int(value * self._DWMr)
        else:
            raise ValueError("Output amplitude should be inside [-1,1] volts.")

    @property
    def offset (self) -> float:
        """Output offset in range [-1,1] vols."""
        return (self.regset.out.cfg_sum / self._DWSr)

    @offset.setter
    def offset (self, value: float):
        if (-1.0 <= value <= 1.0):
            self.regset.out.cfg_sum = int(value * self._DWSr)
        else:
            raise ValueError("Output offset should be inside [-1,1] volts.")

    @property
    def enable (self) -> bool:
        """Output enable boolean value."""
        return (bool(self.regset.out.cfg_ena))

    @enable.setter
    def enable (self, value: bool):
        self.regset.out.cfg_ena = int(value)
