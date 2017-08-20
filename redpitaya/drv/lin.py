from ctypes import *

class lin_mul(object):
    class _regset_t(Structure):
        _fields_ = [('cfg_mul',  c_int32)]  # multiplier (gain)

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.out.cfg_mul = dat_t.unit()

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print("cfg_mul = 0x{reg:08x} = {reg:10d}  # multiplier (gain)\n".format(reg=self.regset.out.cfg_mul))

    @property
    def amplitude(self) -> float:
        """Linear gain."""
        return (self.regset.lin.mul.cfg_mul / float(dat_t.unit()))

    @amplitude.setter
    def amplitude(self, value: float):
        if (dat_t.min() <= value <= dat_t.max()):
            self.regset.lin.mul.cfg_mul = int(value * dat_t.unit())
        else:
            raise ValueError("Linear gain should be inside [{},{}]".format(dat_t.min(), dat_t.max())):

class lin_sum(object):
    class _regset_t(Structure):
        _fields_ = [('cfg_sum',  c_int32)]  # multiplier (gain)

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.lin.sum.cfg_sum = dat_t.zero()

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print("cfg_sum = 0x{reg:08x} = {reg:10d}  # adder (offset)\n".format(reg=self.regset.out.cfg_sum))

    @property
    def offset(self) -> float:
        """Linear offset."""
        return (self.regset.lin.sum.cfg_sum / float(dat_t.unit()))

    @offset.setter
    def offset(self, value: float):
        if (dat_t.min() <= value <= dat_t.max()):
            self.regset.lin.sum.cfg_sum = int(value * dat_t.unit())
        else:
            raise ValueError("Linear offset should be inside [{},{}] volts.".format(dat_t.min(), dat_t.max()))

class lin(lin_mul, lin_sum):
    class _regset_t(Structure):
        _fields_ = [('mul', lin_mul._regset_t),
                    ('sum', lin_sum._regset_t)]

    def default(self):
        """Set registers into default (power-up) state."""
        lin_mul.default(self)
        lin_sum.default(self)

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        lin_mul.show_regset(self)
        lin_sum.show_regset(self)
