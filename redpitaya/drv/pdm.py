from ctypes import *

from .uio import uio


class pdm(uio):

    DN = 4
    DW = 8
    _DWr = 2**DW - 1

    class _regset_t(Structure):
        DN = 4  # TODO: the DN value from the 'pdm' class should be used
        _fields_ = [('pdm', c_uint32 * DN)]

    def __init__(self, uio: str = '/dev/uio/pdm'):
        super().__init__(uio)
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])

    def __del__(self):
        super().__del__()

    def default(self):
        """Set registers into default (power-up) state."""
        for channel in range(self.DN):
            self.regset.pdm[channel] = 0

    def read(self, channel: int) -> int:
        return (self.regset.pdm[channel])

    def write(self, channel: int, value: int):
        if (0 <= value <= self._DWr):
            self.regset.pdm[channel] = value
        else:
            raise ValueError("PDM output value should be in range [0,{}]".format(self._DWr))
