import ctypes
import math
import numpy as np
from scipy import signal

from enum import Enum

import mmap

from .uio import uio
from .evn import evn

class gen (uio, evn):
    # sampling frequency
    FS = 125000000.0
    # linear addition multiplication register width
    DW  = 14
    DWM = 14
    DWS = 14
    # fixed point range
    DWr  = (1 << (DW -1)) - 1
    DWMr = (1 << (DWM-2))
    DWSr = (1 << (DWS-1)) - 1
    # buffer parameters (fixed point number uM.F)
    CWM = 14  # counter width magnitude (fixed point integer)
    CWF = 16  # counter width fraction  (fixed point fraction)
    CW  = CWM + CWF
    # buffer counter ranges
    CWMr = 2**CWM
    CWFr = 2**CWF
    buffer_size = 2**CWM # table size

    # logaritmic scale from 0.116Hz to 62.5Mhz
    f_min = FS / 2**CW
    f_max = FS / 2
    f_one = FS / 2**CWM
    fl_min = math.log10(f_min)
    fl_max = math.log10(f_max)
    fl_one = math.log10(f_one)

    # create waveforms
    t = np.linspace(0, 2*np.pi, buffer_size, endpoint=False)

    def sine (self, t = None):
        if t is None: t = self.t
        return np.sin(t)

    def square (self, duty = 0.5, t = None):
        if t is None: t = self.t
        return signal.square(t, duty)

    def sawtooth (self, width = 0.5, t = None):
        if t is None: t = self.t
        return signal.sawtooth(t, width)

    regset_dtype = np.dtype([
        # control/status
        ('ctl_sts', 'uint32'),
        ('cfg_trg', 'uint32'),  # hardware trigger mask
        # interrupt enable/status
        ('irq_ena', 'uint32'),  # enable
        ('irq_sts', 'uint32'),  # status/clear
        # software event reset/start/stop/trigger masks
        ('cfg_rst', 'uint32'),  # reset
        ('cfg_str', 'uint32'),  # start
        ('cfg_stp', 'uint32'),  # stop
        ('cfg_swt', 'uint32'),  # trigger
        # buffer configuration
        ('cfg_siz', 'uint32'),  # size
        ('cfg_off', 'uint32'),  # offset
        ('cfg_ste', 'uint32'),  # step
        ('rsv_002', 'uint32', 1),
        # burst mode
        ('cfg_bmd', 'uint32'),  # mode [1:0] = [inf, ben]
        ('cfg_bdl', 'uint32'),  # data length
        ('cfg_bln', 'uint32'),  # length (data+pause)
        ('cfg_bnm', 'uint32'),  # number of bursts pulses
        # burst status
        ('sts_bln', 'uint32'),  # length (current position inside burst length)
        ('sts_bnm', 'uint32'),  # number (current burst counter)
        ('rsv_003', 'uint32', 2),
        # linear transformation
        ('cfg_mul',  'int32'),  # multiplier (amplitude)
        ('cfg_sum',  'int32'),  # adder (offset)
        ('cfg_ena', 'uint32')   # output enable
    ])

    def __init__ (self, index:int, uio:str = '/dev/uio/gen'):
        """Module instance index should be provided"""
        # use index
        uio = uio+str(index)

        # call parent class init to open UIO device and mmap maps
        super().__init__(uio)

        # map regset
        regset_array = np.recarray(1, self.regset_dtype, buf=self.uio_mmaps[0])
        self.regset = regset_array[0]
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
        print (
            "ctl_sts = 0x{reg:08x} = {reg:10d}  # control/status                 \n".format(reg=self.regset.ctl_sts)+
            "cfg_trg = 0x{reg:08x} = {reg:10d}  # HW trigger mask                \n".format(reg=self.regset.cfg_trg)+
            "irq_ena = 0x{reg:08x} = {reg:10d}  # interrupt enable               \n".format(reg=self.regset.irq_ena)+
            "irq_sts = 0x{reg:08x} = {reg:10d}  # interrupt status               \n".format(reg=self.regset.irq_sts)+
            "cfg_rst = 0x{reg:08x} = {reg:10d}  # mask reset                     \n".format(reg=self.regset.cfg_rst)+
            "cfg_str = 0x{reg:08x} = {reg:10d}  # mask start                     \n".format(reg=self.regset.cfg_str)+
            "cfg_stp = 0x{reg:08x} = {reg:10d}  # mask stop                      \n".format(reg=self.regset.cfg_stp)+
            "cfg_swt = 0x{reg:08x} = {reg:10d}  # mask trigger                   \n".format(reg=self.regset.cfg_swt)+
            "cfg_siz = 0x{reg:08x} = {reg:10d}  # table size                     \n".format(reg=self.regset.cfg_siz)+
            "cfg_off = 0x{reg:08x} = {reg:10d}  # table offset                   \n".format(reg=self.regset.cfg_off)+
            "cfg_ste = 0x{reg:08x} = {reg:10d}  # table step                     \n".format(reg=self.regset.cfg_ste)+
            "cfg_bmd = 0x{reg:08x} = {reg:10d}  # burst mode [1:0] = [inf, ben]  \n".format(reg=self.regset.cfg_bmd)+
            "cfg_bdl = 0x{reg:08x} = {reg:10d}  # burst data length              \n".format(reg=self.regset.cfg_bdl)+
            "cfg_bln = 0x{reg:08x} = {reg:10d}  # burst length (data+pause)      \n".format(reg=self.regset.cfg_bln)+
            "cfg_bnm = 0x{reg:08x} = {reg:10d}  # burst number of bursts pulses  \n".format(reg=self.regset.cfg_bnm)+
            "sts_bln = 0x{reg:08x} = {reg:10d}  # burst length (current position)\n".format(reg=self.regset.sts_bln)+
            "sts_bnm = 0x{reg:08x} = {reg:10d}  # burst number (current counter) \n".format(reg=self.regset.sts_bnm)+
            "cfg_mul = 0x{reg:08x} = {reg:10d}  # multiplier (amplitude)         \n".format(reg=self.regset.cfg_mul)+
            "cfg_sum = 0x{reg:08x} = {reg:10d}  # adder (offset)                 \n".format(reg=self.regset.cfg_sum)+
            "cfg_ena = 0x{reg:08x} = {reg:10d}  # output enable                  \n".format(reg=self.regset.cfg_ena)
        )

    @property
    def amplitude (self) -> float:
        """Output amplitude in vols"""
        return (self.regset.cfg_mul / self.DWMr)

    @amplitude.setter
    def amplitude (self, value: float):
        # TODO: fix saturation
        if (-1.0 <= value <= 1.0):
            self.regset.cfg_mul = value * self.DWMr
        else:
            raise ValueError("Output amplitude should be inside [-1,1]")

    @property
    def offset (self) -> float:
        """Output offset in vols"""
        return (self.regset.cfg_sum / self.DWSr)

    @offset.setter
    def offset (self, value: float):
        # TODO: fix saturation
        if (-1.0 <= value <= 1.0):
            self.regset.cfg_sum = value * self.DWSr
        else:
            raise ValueError("Output offset should be inside [-1,1]")

    @property
    def enable (self) -> bool:
        """Output enable"""
        return (bool(self.regset.cfg_ena))

    @enable.setter
    def enable (self, value: float):
        self.regset.cfg_ena = int(value)

    @property
    def sample_step (self) -> float:
        """
        Buffer sampling (reading) step:
        if (sample_step = 1) each sample is read exactly once,
        if (sample_step < 1) then at least some samples are repeated,
        if (sample_step > 1) then at least some samples are skipped.
        """
        return ((self.regset.cfg_ste + 1) / self.CWFr)

    @sample_step.setter
    def sample_step (self, value: float):
        if (value < self.CWMr):
            self.regset.cfg_ste = int(value * self.CWFr) - 1
        else:
            raise ValueError("Sampling step should be less then the buffer size. (sample_step < {}".format(self.CWMr))

    @property
    def sample_offset (self) -> float:
        """Buffer sampling (reading) offset."""
        return (self.regset.cfg_off / self.CWFr)

    @sample_offset.setter
    def sample_offset (self, value: float):
        if (value < self.CWMr):
            self.regset.cfg_off = int(value * self.CWFr)
        else:
            raise ValueError("Sampling offset should be less then the buffer size. (sample_offset < {}".format(self.CWMr))

    @property
    def frequency (self) -> float:
        """Frequency in Hz"""
        siz = self.regset.cfg_siz + 1
        stp = self.regset.cfg_ste + 1
        return (stp / siz * self.FS)

    @frequency.setter
    def frequency (self, value: float):
        if (value < self.FS/2):
            siz = self.regset.cfg_siz + 1
            self.regset.cfg_ste = int(siz * (value / self.FS)) - 1
        else:
            raise ValueError("Frequency should be less then half the sample rate. f < FS/2 = {}".format(self.FS/2))

    @property
    def phase (self) -> float:
        """Phase in angular degrees"""
        siz = self.regset.cfg_siz + 1
        off = self.regset.cfg_off
        return (stp / siz * 360)

    @phase.setter
    def phase (self, value: float):
        # TODO add range check
        siz = self.regset.cfg_siz + 1
        self.regset.cfg_off = int(siz * (value % 360) / 360)

    @property
    def waveform (self):
        """Waveworm table containing normalized values in the range [-1,1]"""
        siz = (self.regset.cfg_siz + 1) >> self.CWF
        # TODO: nparray
        return [self.table[i] / self.DWr for i in range(siz)]

    @waveform.setter
    def waveform (self, value):
        # TODO check table size shape
        siz = len(value)
        if (siz <= self.buffer_size):
            for i in range(siz):
                # TODO add saturation
                self.table[i] = int(value[i] * self.DWr)
            self.regset.cfg_siz = (siz << self.CWF) - 1
        else:
            raise ValueError("Waveform table size should not excede buffer size. buffer_size = {}".format(self.buffer_size))

    class modes(Enum):
        CONTINUOUS = 0x0
        FINITE     = 0x1
        INFINITE   = 0x3

    @property
    def mode (self) -> str:
        """
        Generator mode:
            'CONTINUOUS' - non burst mode for periodic signals
            'FINITE'     - finite length bursts
            'INFINITE'   - inifinite length bursts
        """
        return (self.modes(self.regset.cfg_bmd))

    @mode.setter
    def mode (self, value: str):
        if isinstance(value, str):
            self.regset.cfg_bmd = self.modes[value].value
        else:
            raise ValueError("Generator supports modes ['CONTINUOUS', 'FINITE', 'INFINITE']")

    @property
    def burst_repetitions (self) -> int:
        return (self.regset.cfg_bnm + 1)

    @burst_repetitions.setter
    def burst_repetitions (self, value: int):
        # TODO check range
        self.regset.cfg_bnm = value - 1

    @property
    def burst_data_len (self) -> int:
        return (self.regset.cfg_bdl + 1)

    @burst_data_len.setter
    def burst_data_len (self, value: int):
        # TODO check range
        self.regset.cfg_bdl = value - 1

    @property
    def burst_period_len (self) -> int:
        return (self.regset.cfg_bln + 1)

    @burst_period_len.setter
    def burst_period_len (self, value: int):
        # TODO check range
        self.regset.cfg_bln = value - 1
