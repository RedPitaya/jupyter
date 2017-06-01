from ctypes import *
import numpy as np
import math

import mmap

from .evn     import evn
from .acq     import acq
from .la_trg  import la_trg
from .la_msk  import la_msk
from .uio     import uio

class la (evn, acq, la_trg, la_msk, uio):
    #: sampling frequency
    FS = 125000000.0
    #: register width - linear addition multiplication
    DW = 16
    # fixed point range
    _DWr  = (1 << (DW-1)) - 1
    # buffer parameters
    buffer_size = 2**14 #: buffer size
    CW = 31 #: counter size
    _CWr = 2**CW

    class _regset_t (Structure):
        _fields_ = [('evn', evn._regset_t),
                    ('rsv_000', c_uint32),
                    ('acq', acq._regset_t),  # pre/post trigger counters
                    # edge detection
                    ('trg', la_trg._regset_t),
                    # decimation
                    ('cfg_dec', c_uint32),  # decimation factor
                    # mask/polarity
                    ('msk', la_msk._regset_t)]

    def __init__ (self, uio:str = '/dev/uio/la'):
        # call parent class init to open UIO device and map regset
        super().__init__(uio)

        # map regset
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])
        # map buffer table
        self.table = np.frombuffer(self.uio_mmaps[1], 'int16')
    def __del__ (self):
        # call parent class init to unmap maps and close UIO device
        super().__del__()

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        evn.show_regset(self)
        acq.show_regset(self)
        la_trg.show_regset(self)
        print (
            "cfg_dec = 0x{reg:08x} = {reg:10d}  # decimation factor         \n".format(reg=self.regset.cfg_dec)
        )
        la_msk.show_regset(self)

    @property
    def decimation (self) -> int:
        """Decimation factor."""
        return (self.regset.cfg_dec + 1)

    @decimation.setter
    def decimation (self, value: int):
        # TODO check range
        self.regset.cfg_dec = value - 1

    @property
    def sample_rate (self) -> float:
        """Sample rate depending on decimation factor."""
        return (self.FS / self.decimation)

    @property
    def sample_period (self) -> float:
        """Sample period depending on decimation factor."""
        return (1 / self.sample_rate)

    @property
    def pointer (self):
        # mask out overflow bit and sum pre and post trigger counters
        cnt = self.trigger_pre_status + self.trigger_post_status
        adr = cnt % self.buffer_size
        return adr

    def data(self, siz: int = buffer_size, ptr: int = None) -> np.array:
        """Data.

        Parameters
        ----------
        siz : int, optional
            Number of data samples to be read from the FPGA buffer.
        ptr : int, optional
            End of data pointer, only use if you understand
            the source code.

        Returns
        -------
        array
            Array containing binary samples.
            The data is alligned at the end to the last sample
            stored into the buffer.
        """
        if ptr is None:
            ptr = int(self.pointer)
        adr = (self.buffer_size + ptr - siz) % self.buffer_size
        # TODO: avoid making copy of entire array
        table = np.roll(self.table, -ptr)
        return table.astype('uint16')[-siz:]
