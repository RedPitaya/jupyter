from ctypes import *


class la_rle(object):
    class _regset_t(Structure):
        _fields_ = [('cfg_rle', c_uint32),  # RLE mode
                    ('cfg_cur', c_uint32),  # current counter
                    ('cfg_lst', c_uint32)]  # last    counter

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.rle.cfg_rle = 0

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print(
            "cfg_rle = 0x{reg:08x} = {reg:10d}  # RLE mode       \n".format(reg = self.regset.rle.cfg_rle) +
            "cfg_cur = 0x{reg:08x} = {reg:10d}  # current counter\n".format(reg = self.regset.rle.cfg_cur) +
            "cfg_lst = 0x{reg:08x} = {reg:10d}  # last    counter\n".format(reg = self.regset.rle.cfg_lst)
        )

    @property
    def rle(self) -> bool:
        """RLE mode enable."""
        return bool(self.regset.rle.cfg_rle)

    @rle.setter
    def rle(self, value: bool):
        self.regset.rle.cfg_rle = int(value)

    @property
    def counter_current(self) -> int:
        """Current data stream length counter."""
        return self.regset.rle.cfg_cur

    @property
    def counter_last(self) -> int:
        """Last data stream length counter."""
        return self.regset.rle.cfg_lst
