from ctypes import *
import numpy as np
import math

import mmap

from .uio import uio
from .evn import evn

class osc (uio, evn):
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
        _fields_ = [# control/status
                    ('ctl_sts', c_uint32    ),
                    ('cfg_evn', c_uint32    ),  # software event source select
                    ('cfg_trg', c_uint32    ),  # hardware trigger mask
                    ('rsv_000', c_uint32 * 1),
                    # pre/post trigger counters
                    ('cfg_pre', c_uint32    ),  # configuration pre  trigger
                    ('cfg_pst', c_uint32    ),  # configuration post trigger
                    ('sts_pre', c_uint32    ),  # status pre  trigger
                    ('sts_pst', c_uint32    ),  # status post trigger
                    # edge detection
                    ('cfg_neg',  c_int32    ),  # negative level
                    ('cfg_pos',  c_int32    ),  # positive level
                    ('cfg_edg', c_uint32    ),  # edge (0-pos, 1-neg)
                    ('cfg_hld', c_uint32    ),  # hold off time
                    # decimation
                    ('cfg_dec', c_uint32    ),  # decimation factor
                    ('cfg_shr', c_uint32    ),  # shift right
                    ('cfg_avg', c_uint32    ),  # average enable
                    # filter
                    ('cfg_byp', c_uint32    ),  # bypass
                    ('cfg_faa',  c_int32    ),  # AA coeficient
                    ('cfg_fbb',  c_int32    ),  # BB coeficient
                    ('cfg_fkk',  c_int32    ),  # KK coeficient
                    ('cfg_fpp',  c_int32    )]  # PP coeficient

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
        print (
            "ctl_sts = 0x{reg:08x} = {reg:10d}  # control/status            \n".format(reg=self.regset.ctl_sts)+
            "cfg_evn = 0x{reg:08x} = {reg:10d}  # SW event source select    \n".format(reg=self.regset.cfg_evn)+
            "cfg_trg = 0x{reg:08x} = {reg:10d}  # HW trigger mask           \n".format(reg=self.regset.cfg_trg)+
            "cfg_pre = 0x{reg:08x} = {reg:10d}  # delay pre  trigger        \n".format(reg=self.regset.cfg_pre)+
            "cfg_pst = 0x{reg:08x} = {reg:10d}  # delay post trigger        \n".format(reg=self.regset.cfg_pst)+
            "sts_pre = 0x{reg:08x} = {reg:10d}  # status pre  trigger       \n".format(reg=self.regset.sts_pre)+
            "sts_pst = 0x{reg:08x} = {reg:10d}  # status post trigger       \n".format(reg=self.regset.sts_pst)+
            "cfg_neg = 0x{reg:08x} = {reg:10d}  # negative level            \n".format(reg=self.regset.cfg_neg)+
            "cfg_pos = 0x{reg:08x} = {reg:10d}  # positive level            \n".format(reg=self.regset.cfg_pos)+
            "cfg_edg = 0x{reg:08x} = {reg:10d}  # edge (0-pos, 1-neg)       \n".format(reg=self.regset.cfg_edg)+
            "cfg_hld = 0x{reg:08x} = {reg:10d}  # hold off time             \n".format(reg=self.regset.cfg_hld)+
            "cfg_dec = 0x{reg:08x} = {reg:10d}  # decimation factor         \n".format(reg=self.regset.cfg_dec)+
            "cfg_shr = 0x{reg:08x} = {reg:10d}  # shift right               \n".format(reg=self.regset.cfg_shr)+
            "cfg_avg = 0x{reg:08x} = {reg:10d}  # average enable            \n".format(reg=self.regset.cfg_avg)+
            "cfg_byp = 0x{reg:08x} = {reg:10d}  # bypass                    \n".format(reg=self.regset.cfg_byp)+
            "cfg_faa = 0x{reg:08x} = {reg:10d}  # AA coeficient             \n".format(reg=self.regset.cfg_faa)+
            "cfg_fbb = 0x{reg:08x} = {reg:10d}  # BB coeficient             \n".format(reg=self.regset.cfg_fbb)+
            "cfg_fkk = 0x{reg:08x} = {reg:10d}  # KK coeficient             \n".format(reg=self.regset.cfg_fkk)+
            "cfg_fpp = 0x{reg:08x} = {reg:10d}  # PP coeficient             \n".format(reg=self.regset.cfg_fpp)
        )

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
    def trigger_pre (self) -> int:
        """Pre trigger delay.

        Number of samples stored into the buffer
        after start() before a trigger event is accepted.
        It makes sense for this number to be up to buffer size.
        """
        return (self.regset.cfg_pre)

    @trigger_pre.setter
    def trigger_pre (self, value: int):
        if (value < self._CWr):
            self.regset.cfg_pre = value
        else:
            raise ValueError("Pre trigger delay should be less or equal to {}.".format(self._CWr))

    @property
    def trigger_post (self) -> int:
        """Post trigger delay.

        Number of samples stored into the buffer
        after a trigger, before writing stops automatically.
        It makes sense for this number to be up to buffer size.
        """
        return (self.regset.cfg_pst)

    @trigger_post.setter
    def trigger_post (self, value: int):
        if (value < self._CWr):
            self.regset.cfg_pst = value
        else:
            raise ValueError("Post trigger delay should be less or equal to {}.".format(self._CWr))
        # TODO check range

    @property
    def trigger_pre_status (self) -> int:
        """Pre trigger sample counter status."""
        return (self.regset.sts_pre)

    @property
    def trigger_post_status (self) -> int:
        """Post trigger sample counter status."""
        return (self.regset.sts_pst)

    @property
    def level (self) -> float:
        """Trigger level in vols, or a pair of values [neg, pos] if a hysteresis is desired."""
        scale = self.__input_range / self._DWr
        return ([self.regset.cfg_neg * scale, self.regset.cfg_pos * scale])

    @level.setter
    def level (self, value: tuple):
        scale = self._DWr / self.__input_range
        if isinstance(value, float):
            value = [value]*2
        if (-1.0 <= value[0] <= 1.0):
            self.regset.cfg_neg = int(value[0] * scale)
        else:
            raise ValueError("Trigger negative level should be inside [{},{}]".format(self.__input_range))
        if (-1.0 <= value[1] <= 1.0):
            self.regset.cfg_pos = int(value[1] * scale)
        else:
            raise ValueError("Trigger positive level should be inside [{},{}]".format(self.__input_range))

    @property
    def edge (self) -> str:
        """Trigger edge as a string 'pos'/'neg'"""
        return (('pos', 'neg')[self.regset.cfg_edg])

    @edge.setter
    def edge (self, value: str):
        if (value in self._edges):
            self.regset.cfg_edg = self._edges[value]
        else:
            raise ValueError("Trigger edge should be one of {}".format(list(self._edges.keys())))

    @property
    def holdoff (self) -> int:
        """Trigger hold off time in clock periods"""
        return self.regset.cfg_hld

    @holdoff.setter
    def holdoff (self, value: int):
        # TODO: check range
        self.regset.cfg_hld = value

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
    def filter_bypass (self) -> bool:
        """Bypass digital input filter.

        True   filter is not used
        False  filter is used
        """
        return (bool(self.regset.cfg_byp))

    @filter_bypass.setter
    def filter_bypass (self, value: bool):
        self.regset.cfg_byp = int(value)

    @property
    def filter_coeficients (self) -> tuple:
        return (self.regset.cfg_faa,
                self.regset.cfg_fbb,
                self.regset.cfg_fkk,
                self.regset.cfg_fpp)

    @filter_coeficients.setter
    def filter_coeficients (self, value: tuple):
        # TODO check range
        self.regset.cfg_faa = value[0]
        self.regset.cfg_fbb = value[1]
        self.regset.cfg_fkk = value[2]
        self.regset.cfg_fpp = value[3]

    @property
    def pointer (self):
        # mask out overflow bit and sum pre and post trigger counters
        cnt = ( (self.regset.sts_pre & 0x7fffffff)
              + (self.regset.sts_pst & 0x7fffffff) )
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
