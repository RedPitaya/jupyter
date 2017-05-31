from ctypes import *
import numpy as np

from enum import Enum

import mmap

from .evn     import evn
from .asg_bst import asg_bst
from .uio     import uio

class gen (evn, asg_bst, uio):
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
    # buffer parameters (fixed point number uM.F)
    CWM = 14  #: counter width - magnitude (fixed point integer)
    CWF = 16  #: counter width - fraction  (fixed point fraction)
    CW  = CWM + CWF
    # buffer counter ranges
    _CWMr = 2**CWM
    _CWFr = 2**CWF
    buffer_size = 2**CWM #: table size
    # burst counter parameters
    CWR = 14  #: counter width - burst data repetition
    CWL = 32  #: counter width - burst period length
    CWN = 16  #: counter width - burst period number
    _CWRr = 2**CWR
    _CWLr = 2**CWL
    _CWNr = 2**CWN

    # logaritmic scale from 0.116Hz to 62.5Mhz
    _f_min = FS / 2**CW
    _f_max = FS / 2
    _f_one = FS / 2**CWM

    class _regset_t (Structure):
        _fields_ = [('evn', evn._regset_t),
                    ('rsv_000', c_uint32),
                    ('cfg_bmd', c_uint32),  # mode [1:0] = [inf, ben]
                    ('per', asg_per._regset_t),
                    ('bst', asg_bst._regset_t),
                    ('rsv_001', c_uint32 * 2),
                    ('out', gen_out._regset_t)]

    def __init__ (self, index: int, uio: str = '/dev/uio/gen'):
        """Module instance index should be provided"""

        # use index
        uio = uio+str(index)

        # call parent class init to open UIO device and mmap maps
        super().__init__(uio)

        # map regset
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])
        # map buffer table
        self.table = np.frombuffer(self.uio_mmaps[1], 'int32')

    def __del__ (self):
        # disable output
        self.enable = False
        # make sure state machine is not running
        self.reset()
        # call parent class init to unmap maps and close UIO device
        super().__del__()

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        evn.show_regset(self)
        print (
            "cfg_bmd = 0x{reg:08x} = {reg:10d}  # burst mode [1:0] = [inf, ben]  \n".format(reg=self.regset.cfg_bmd)
        )
        asg_bst.show_regset(self)
        gen_out.show_regset(self)

    @property
    def waveform (self):
        """Waveworm array containing normalized values in the range [-1,1].

        Array can be up to `buffer_size` samples in length.
        """
        siz = self.table_size
        # TODO: nparray
        return [self.table[i] / self._DWr for i in range(siz)]

    @waveform.setter
    def waveform (self, value):
        siz = len(value)
        if (siz <= self.buffer_size):
            for i in range(siz):
                # TODO add saturation
                self.table[i] = int(value[i] * self._DWr)
            self.table_size = siz
        else:
            raise ValueError("Waveform table size should not excede buffer size. buffer_size = {}".format(self.buffer_size))

    class modes(Enum):
        FINITE     = 0x1
        INFINITE   = 0x3

    @property
    def mode (self) -> str:
        """Logic generator mode:

        * 'FINITE'     - finite    length bursts
        * 'INFINITE'   - inifinite length bursts
        """
        return (self.modes(self.regset.cfg_bmd))

    @mode.setter
    def mode (self, value: str):
        if isinstance(value, str):
            self.regset.cfg_bmd = self.modes[value].value
        else:
            raise ValueError("Generator supports modes ['CONTINUOUS', 'FINITE', 'INFINITE'].")
