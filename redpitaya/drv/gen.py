from ctypes import *
import numpy as np

from enum import Enum

import mmap

from .evn     import evn
from .asg_per import asg_per
from .asg_bst import asg_bst
from .gen_out import gen_out
from .wave    import wave
from .uio     import uio


class gen(evn, asg_per, asg_bst, gen_out, wave, uio):
    """
    Generator FPGA module driver.
    """

    #: sampling frequency
    FS = 125000000.0
    # linear addition multiplication register width
    DW  = 14  #: data width - streaming sample
    DWM = 14  #: data width - linear gain multiplier
    DWS = 14  #: data width - linear offset summand
    # fixed point range
    _DWr  = (1 << (DW -1)) - 1
    _DWMr = (1 << (DWM-2))
    _DWSr = (1 << (DWS-1)) - 1

    class _regset_t(Structure):
        _fields_ = [('evn', evn._regset_t),
                    ('rsv_000', c_uint32),
                    ('cfg_bmd', c_uint32),  # mode [1:0] = [inf, ben]
                    ('per', asg_per._regset_t),
                    ('bst', asg_bst._regset_t),
                    ('rsv_001', c_uint32 * 2),
                    ('out', gen_out._regset_t)]

    def __init__(self, index: int, uio: str = '/dev/uio/gen'):
        """Module instance index should be provided"""

        # use index
        uio = uio+str(index)

        # call parent class init to open UIO device and mmap maps
        super().__init__(uio)

        # map regset
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])
        # map buffer table
        self.table = np.frombuffer(self.uio_mmaps[1], 'int32')

        # calculate constants
        self.buffer_size = 2**self.CWM  #: table size

        # logaritmic scale from 0.116Hz to 62.5Mhz
        _f_min = self.FS / 2**self.CW
        _f_max = self.FS / 2
        _f_one = self.FS / 2**self.CWM

    def __del__(self):
        # disable output
        self.enable = False
        # make sure state machine is not running
        self.reset()
        # call parent class init to unmap maps and close UIO device
        super().__del__()

    def default(self):
        """Set registers into default (power-up) state."""
        evn.default(self)
        self.regset.cfg_bmd = 0
        asg_per.default(self)
        asg_bst.default(self)
        gen_out.default(self)

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        evn.show_regset(self)
        print(
            "cfg_bmd = 0x{reg:08x} = {reg:10d}  # burst mode [1:0] = [inf, ben]  \n".format(reg = self.regset.cfg_bmd)
        )
        asg_per.show_regset(self)
        asg_bst.show_regset(self)
        gen_out.show_regset(self)

    @property
    def waveform(self):
        """Waveworm array containing normalized values in the range [-1,1].

        Array can be up to `buffer_size` samples in length.
        """
        siz = self.table_size
        # TODO: nparray
        return [self.table[i] / self._DWr for i in range(siz)]

    @waveform.setter
    def waveform(self, value):
        siz = len(value)
        if (siz <= self.buffer_size):
            for i in range(siz):
                # TODO add saturation
                self.table[i] = int(value[i] * self._DWr)
            self.table_size = siz
        else:
            raise ValueError("Waveform table size should not excede buffer size. buffer_size = {}".format(self.buffer_size))

    class modes(Enum):
        CONTINUOUS = 0x0
        FINITE     = 0x1
        INFINITE   = 0x3

    @property
    def mode(self) -> str:
        """Generator mode:

        * 'CONTINUOUS' - non burst mode for continuous/periodic signals
        * 'FINITE'     - finite    length bursts
        * 'INFINITE'   - inifinite length bursts
        """
        return (self.modes(self.regset.cfg_bmd))

    @mode.setter
    def mode(self, value: str):
        if isinstance(value, str):
            self.regset.cfg_bmd = self.modes[value].value
        else:
            raise ValueError("Generator supports modes ['CONTINUOUS', 'FINITE', 'INFINITE'].")
