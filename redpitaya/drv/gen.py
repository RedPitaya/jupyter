import ctypes
import math
import numpy as np

from enum import Enum

import mmap

from .uio import uio
from .evn import evn
from .wave import wave

class gen (uio, evn, wave):
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

    _regset_dtype = np.dtype([
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
        # generator mode
        ('cfg_bmd', 'uint32'),  # mode [1:0] = [inf, ben]
        # continuous/periodic configuration
        ('cfg_siz', 'uint32'),  # size
        ('cfg_off', 'uint32'),  # offset
        ('cfg_ste', 'uint32'),  # step
        # burst configuration
        ('cfg_bdr', 'uint32'),  # burst data   repetitions
        ('cfg_bdl', 'uint32'),  # burst data   length
        ('cfg_bpl', 'uint32'),  # burst period length (data+pause)
        ('cfg_bpn', 'uint32'),  # burst period number
        # burst status
        ('sts_bln', 'uint32'),  # length (current position inside burst length)
        ('sts_bnm', 'uint32'),  # number (current burst counter)
        ('rsv_003', 'uint32', 2),
        # linear transformation
        ('cfg_mul',  'int32'),  # multiplier (amplitude)
        ('cfg_sum',  'int32'),  # adder (offset)
        ('cfg_ena', 'uint32')   # output enable
    ])

    def __init__ (self, index: int, uio: str = '/dev/uio/gen'):
        """Module instance index should be provided"""

        # use index
        uio = uio+str(index)

        # call parent class init to open UIO device and mmap maps
        super().__init__(uio)

        # map regset
        regset_array = np.recarray(1, self._regset_dtype, buf=self.uio_mmaps[0])
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
        """Print FPGA module register set for debugging purposes."""
        print (
            "ctl_sts = 0x{reg:08x} = {reg:10d}  # control/status                 \n".format(reg=self.regset.ctl_sts)+
            "cfg_trg = 0x{reg:08x} = {reg:10d}  # HW trigger mask                \n".format(reg=self.regset.cfg_trg)+
            "irq_ena = 0x{reg:08x} = {reg:10d}  # interrupt enable               \n".format(reg=self.regset.irq_ena)+
            "irq_sts = 0x{reg:08x} = {reg:10d}  # interrupt status               \n".format(reg=self.regset.irq_sts)+
            "cfg_rst = 0x{reg:08x} = {reg:10d}  # mask reset                     \n".format(reg=self.regset.cfg_rst)+
            "cfg_str = 0x{reg:08x} = {reg:10d}  # mask start                     \n".format(reg=self.regset.cfg_str)+
            "cfg_stp = 0x{reg:08x} = {reg:10d}  # mask stop                      \n".format(reg=self.regset.cfg_stp)+
            "cfg_swt = 0x{reg:08x} = {reg:10d}  # mask trigger                   \n".format(reg=self.regset.cfg_swt)+
            "cfg_bmd = 0x{reg:08x} = {reg:10d}  # burst mode [1:0] = [inf, ben]  \n".format(reg=self.regset.cfg_bmd)+
            "cfg_siz = 0x{reg:08x} = {reg:10d}  # table size                     \n".format(reg=self.regset.cfg_siz)+
            "cfg_off = 0x{reg:08x} = {reg:10d}  # table offset                   \n".format(reg=self.regset.cfg_off)+
            "cfg_ste = 0x{reg:08x} = {reg:10d}  # table step                     \n".format(reg=self.regset.cfg_ste)+
            "cfg_bdr = 0x{reg:08x} = {reg:10d}  # burst data   repetition        \n".format(reg=self.regset.cfg_bdr)+
            "cfg_bdl = 0x{reg:08x} = {reg:10d}  # burst data   length            \n".format(reg=self.regset.cfg_bdl)+
            "cfg_bpl = 0x{reg:08x} = {reg:10d}  # burst period length            \n".format(reg=self.regset.cfg_bpl)+
            "cfg_bpn = 0x{reg:08x} = {reg:10d}  # burst period number            \n".format(reg=self.regset.cfg_bpn)+
            "sts_bln = 0x{reg:08x} = {reg:10d}  # burst length (current position)\n".format(reg=self.regset.sts_bln)+
            "sts_bnm = 0x{reg:08x} = {reg:10d}  # burst number (current counter) \n".format(reg=self.regset.sts_bnm)+
            "cfg_mul = 0x{reg:08x} = {reg:10d}  # multiplier (amplitude)         \n".format(reg=self.regset.cfg_mul)+
            "cfg_sum = 0x{reg:08x} = {reg:10d}  # adder (offset)                 \n".format(reg=self.regset.cfg_sum)+
            "cfg_ena = 0x{reg:08x} = {reg:10d}  # output enable                  \n".format(reg=self.regset.cfg_ena)
        )

    @property
    def amplitude (self) -> float:
        """Output amplitude in range [-1,1] vols."""
        return (self.regset.cfg_mul / self._DWMr)

    @amplitude.setter
    def amplitude (self, value: float):
        if (-1.0 <= value <= 1.0):
            self.regset.cfg_mul = value * self._DWMr
        else:
            raise ValueError("Output amplitude should be inside [-1,1] volts.")

    @property
    def offset (self) -> float:
        """Output offset in range [-1,1] vols."""
        return (self.regset.cfg_sum / self._DWSr)

    @offset.setter
    def offset (self, value: float):
        if (-1.0 <= value <= 1.0):
            self.regset.cfg_sum = value * self._DWSr
        else:
            raise ValueError("Output offset should be inside [-1,1] volts.")

    @property
    def enable (self) -> bool:
        """Output enable boolean value."""
        return (bool(self.regset.cfg_ena))

    @enable.setter
    def enable (self, value: bool):
        self.regset.cfg_ena = int(value)

    @property
    def sample_offset (self) -> float:
        """Buffer sampling (reading) offset.

        Offset should be less then the waveform array length.
        """
        return (self.regset.cfg_off / self._CWFr)

    @sample_offset.setter
    def sample_offset (self, value: float):
        if (value < self._CWMr):
            self.regset.cfg_off = int(value * self._CWFr)
        else:
            raise ValueError("Sampling offset should be less then the buffer size. (sample_offset < {}".format(self._CWMr))

    @property
    def frequency (self) -> float:
        """Periodic signal frequency up to FS/2"""
        siz = self.regset.cfg_siz + 1
        stp = self.regset.cfg_ste + 1
        return (stp / siz * self.FS)

    @frequency.setter
    def frequency (self, value: float):
        if (value < self.FS/2):
            siz = self.regset.cfg_siz + 1
            self.regset.cfg_ste = int(siz * (value / self.FS)) - 1
        else:
            raise ValueError("Frequency should be less then half the sample rate. f < FS/2 = {} Hz".format(self.FS/2))

    @property
    def phase (self) -> float:
        """Periodic signal phase in angular degrees"""
        siz = self.regset.cfg_siz + 1
        off = self.regset.cfg_off
        return (off / siz * 360)

    @phase.setter
    def phase (self, value: float):
        siz = self.regset.cfg_siz + 1
        self.regset.cfg_off = int(siz * (value % 360) / 360)

    @property
    def waveform (self):
        """Waveworm array containing normalized values in the range [-1,1].

        Array can be up to `buffer_size` samples in length.
        """
        siz = (self.regset.cfg_siz + 1) >> self.CWF
        # TODO: nparray
        return [self.table[i] / self._DWr for i in range(siz)]

    @waveform.setter
    def waveform (self, value):
        siz = len(value)
        if (siz <= self.buffer_size):
            for i in range(siz):
                # TODO add saturation
                self.table[i] = int(value[i] * self._DWr)
            self.regset.cfg_siz = (siz << self.CWF) - 1
        else:
            raise ValueError("Waveform table size should not excede buffer size. buffer_size = {}".format(self.buffer_size))

    class modes(Enum):
        CONTINUOUS = 0x0
        FINITE     = 0x1
        INFINITE   = 0x3

    @property
    def mode (self) -> str:
        """Generator mode:

        * 'CONTINUOUS' - non burst mode for continuous/periodic signals
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

    @property
    def burst_data_repetitions (self) -> int:
        """Burst data repetitions, up to 2**`CWL`."""
        return (self.regset.cfg_bdr + 1)

    @burst_data_repetitions.setter
    def burst_data_repetitions (self, value: int):
        if (value < self._CWRr):
            self.regset.cfg_bdr = value - 1
        else:
            raise ValueError("Burst data repetitions should be less or equal to {}.".format(self._CWRr))

    @property
    def burst_data_length (self) -> int:
        """Burst data length, up to waveform array size."""
        return (self.regset.cfg_bdl + 1)

    @burst_data_length.setter
    def burst_data_length (self, value: int):
        if (value < self._CWMr):
            self.regset.cfg_bdl = value - 1
        else:
            raise ValueError("Burst data length should be less or equal to {}.".format(self._CWMr))

    @property
    def burst_period_length (self) -> int:
        """Burst period length (data+pause), up to 2**`CWL`."""
        return (self.regset.cfg_bpl + 1)

    @burst_period_length.setter
    def burst_period_length (self, value: int):
        if (value < self._CWLr):
            self.regset.cfg_bpl = value - 1
        else:
            raise ValueError("Burst period length should be less or equal to {}.".format(self._CWLr))

    @property
    def burst_period_number (self) -> int:
        """Number of burst period reperitions, up to 2**`CWN`."""
        return (self.regset.cfg_bpn + 1)

    @burst_period_number.setter
    def burst_period_number (self, value: int):
        if (value < self._CWNr):
            self.regset.cfg_bpn = value - 1
        else:
            raise ValueError("Burst period number should be less or equal to {}.".format(self._CWNr))
