from ctypes import *
import numpy as np
import math

import mmap

from .evn     import evn
from .acq     import acq
from .osc_trg import osc_trg
from .osc_fil import osc_fil
from .uio     import uio

class osc (evn, acq, osc_trg, osc_fil, uio):
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

    # trigger edge dictionary
    _edges = {'pos': 0, 'neg': 1}
    #: analog stage range voltages
    ranges = (1.0, 20.0)
    # filter coeficients
    _filters = { 1.0: (0x7D93, 0x437C7, 0xd9999a, 0x2666),
                20.0: (0x4C5F, 0x2F38B, 0xd9999a, 0x2666)}

    class _regset_t (Structure):
        _fields_ = [('evn', evn._regset_t),
                    ('rsv_000', c_uint32),
                    ('acq', acq._regset_t),  # pre/post trigger counters
                    # edge detection
                    ('trg', osc_trg._regset_t),
                    # decimation
                    ('cfg_dec', c_uint32),  # decimation factor
                    ('cfg_shr', c_uint32),  # shift right
                    ('cfg_avg', c_uint32),  # average enable
                    # filter
                    ('fil', osc_fil._regset_t)]

    def __init__ (self, index:int, input_range:float, uio:str = '/dev/uio/osc'):
        """Module instance index should be provided"""

        # use index
        uio = uio+str(index)

        # call parent class init to open UIO device and map regset
        super().__init__(uio)

        # map regset
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])
        # map buffer table
        self.table = np.frombuffer(self.uio_mmaps[1], 'int16')

        # set input range (there is no default)
        self.input_range = input_range

    def __del__ (self):
        # call parent class init to unmap maps and close UIO device
        super().__del__()

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        evn.show_regset(self)
        acq.show_regset(self)
        osc_trg.show_regset(self)
        print (
            "cfg_dec = 0x{reg:08x} = {reg:10d}  # decimation factor         \n".format(reg=self.regset.cfg_dec)+
            "cfg_shr = 0x{reg:08x} = {reg:10d}  # shift right               \n".format(reg=self.regset.cfg_shr)+
            "cfg_avg = 0x{reg:08x} = {reg:10d}  # average enable            \n".format(reg=self.regset.cfg_avg)
        )
        osc_fil.show_regset(self)

    @property
    def input_range (self) -> float:
        """Input range can be one of the supporte ranges.

        See HW board documentation for details.
        """
        return (self.__input_range)

    @input_range.setter
    def input_range (self, value: float):
        if value in self.ranges:
            self.__input_range = value
            self.filter_coeficients = self._filters[value]
        else:
            raise ValueError("Input range can be one of {} volts.".format(self.ranges))

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
    def average (self) -> bool:
        # TODO units should be secconds
        return (bool(self.regset.cfg_avg))

    @average.setter
    def average (self, value: bool):
        # TODO check range, for non 2**n decimation factors,
        # scaling should be applied in addition to shift
        self.regset.cfg_avg = int(value)
        self.regset.cfg_shr = math.ceil(math.log2(self.decimation))

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
            Array containing float samples scaled
            to the selected analog range.
            The data is alligned at the end to the last sample
            stored into the buffer.
        """
        if ptr is None:
            ptr = int(self.pointer)
        adr = (self.buffer_size + ptr - siz) % self.buffer_size
        # TODO: avoid making copy of entire array
        table = np.roll(self.table, -ptr)
        return table.astype('float32')[-siz:] * (self.__input_range / self._DWr)
