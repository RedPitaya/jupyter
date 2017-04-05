import numpy as np

import mmap

from .uio import uio
from .evn import evn

class osc (uio, evn):
    # sampling frequency
    FS = 125000000.0
    # linear addition multiplication register width
    DW = 16
    # fixed point range
    DWr  = (1 << (DW-1)) - 1
    # buffer parameters
    N = 2**14 # table size

    # trigger edge dictionary
    edges = {'positive': 0, 'negative': 1,
             'pos'     : 0, 'neg'     : 1,
             'p'       : 0, 'n'       : 1,
             '+'       : 0, '-'       : 1}
    # analog stage range voltages
    ranges = (1.0, 20.0)
    # filter coeficients
    filters = { 1.0: (0x7D93, 0x437C7, 0xd9999a, 0x2666),
               20.0: (0x4C5F, 0x2F38B, 0xd9999a, 0x2666)}

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
        # pre/post trigger counters
        ('cfg_pre', 'uint32'),  # configuration pre  trigger
        ('cfg_pst', 'uint32'),  # configuration post trigger
        ('sts_pre', 'uint32'),  # status pre  trigger
        ('sts_pst', 'uint32'),  # status post trigger
        # edge detection
        ('cfg_neg',  'int32'),  # negative level
        ('cfg_pos',  'int32'),  # positive level
        ('cfg_edg', 'uint32'),  # edge (0-pos, 1-neg)
        ('cfg_hld', 'uint32'),  # hold off time
        # decimation
        ('cfg_dec', 'uint32'),  # decimation factor
        ('cfg_shr', 'uint32'),  # shift right
        ('cfg_avg', 'uint32'),  # average enable
        # filter
        ('cfg_byp', 'uint32'),  # bypass
        ('cfg_faa',  'int32'),  # AA coeficient
        ('cfg_fbb',  'int32'),  # BB coeficient
        ('cfg_fkk',  'int32'),  # KK coeficient
        ('cfg_fpp',  'int32')   # PP coeficient
    ])

    def __init__ (self, index:int, input_range:float, uio:str = '/dev/uio/osc'):
        """Module instance index should be provided"""

        # use index
        uio = uio+str(index)

        # call parent class init to open UIO device and map regset
        super().__init__(uio)

        # map buffer table
        try:
            self.uio_tbl = mmap.mmap(
                # TODO: probably the length should be rounded up to mmap.PAGESIZE
                fileno=self.uio_dev, length=2*self.N, offset=mmap.PAGESIZE,
                flags=mmap.MAP_SHARED, prot=(mmap.PROT_READ | mmap.PROT_WRITE))
        except OSError as e:
            raise IOError(e.errno, "Mapping (buffer) {}: {}".format(uio, e.strerror))

        #table_array = np.recarray(1, self.table_dtype, buf=self.uio_tbl)
        self.table = np.frombuffer(self.uio_tbl, 'int16')

        # set input range (there is no default)
        self.input_range = input_range

    def __del__ (self):
        self.uio_tbl.close()
        # call parent class init to unmap regset and close UIO device
        super().__del__()

    def show_regset (self):
        print (
            "ctl_sts = 0x{reg:08x} = {reg:10d}  # control/status            \n".format(reg=self.regset.ctl_sts)+
            "cfg_trg = 0x{reg:08x} = {reg:10d}  # HW trigger mask           \n".format(reg=self.regset.cfg_trg)+
            "irq_ena = 0x{reg:08x} = {reg:10d}  # interrupt enable          \n".format(reg=self.regset.irq_ena)+
            "irq_sts = 0x{reg:08x} = {reg:10d}  # interrupt status          \n".format(reg=self.regset.irq_sts)+
            "cfg_rst = 0x{reg:08x} = {reg:10d}  # mask reset                \n".format(reg=self.regset.cfg_rst)+
            "cfg_str = 0x{reg:08x} = {reg:10d}  # mask start                \n".format(reg=self.regset.cfg_str)+
            "cfg_stp = 0x{reg:08x} = {reg:10d}  # mask stop                 \n".format(reg=self.regset.cfg_stp)+
            "cfg_swt = 0x{reg:08x} = {reg:10d}  # mask trigger              \n".format(reg=self.regset.cfg_swt)+
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
        return (self.__input_range)

    @input_range.setter
    def input_range (self, value: float):
        if value in self.ranges:
            self.__input_range = value
            self.filter_coeficients = self.filters[value]
        else:
            raise ValueError("Input range can be one of {} volts.".format(self.ranges))

    @property
    def trigger_pre (self) -> float:
        return (self.regset.cfg_pre * self.sample_period)

    @trigger_pre.setter
    def trigger_pre (self, value: float):
        cnt = int(value / self.sample_period)
        # TODO check range
        self.regset.cfg_pre = cnt

    @property
    def trigger_post (self) -> float:
        return (self.regset.cfg_pst * self.sample_period)

    @trigger_post.setter
    def trigger_post (self, value: float):
        cnt = int(value / self.sample_period)
        # TODO check range
        self.regset.cfg_pst = cnt

    @property
    def trigger_pre_status (self) -> float:
        return (self.regset.sts_pre * self.sample_period)

    @property
    def trigger_post_status (self) -> float:
        return (self.regset.sts_pst * self.sample_period)

    @property
    def level (self) -> float:
        """Trigger level in vols [neg, pos]"""
        scale = self.__input_range / self.DWr
        return ([self.regset.cfg_neg * scale, self.regset.cfg_pos * scale])

    @level.setter
    def level (self, value: tuple):
        """Trigger level in vols [neg, pos]"""
        scale = self.DWr / self.__input_range
        if (-1.0 <= value[0] <= 1.0):
            self.regset.cfg_neg = value[0] * scale
        else:
            raise ValueError("Trigger negative level should be inside [{},{}]".format(self.__input_range))
        if (-1.0 <= value[1] <= 1.0):
            self.regset.cfg_pos = value[1] * scale
        else:
            raise ValueError("Trigger positive level should be inside [{},{}]".format(self.__input_range))

    @property
    def edge (self) -> str:
        """Trigger edge as a string 'pos'/'neg'"""
        return (['pos', 'neg'][self.regset.cfg_edg])

    @edge.setter
    def edge (self, value: str):
        """Trigger edge as a string 'pos'/'neg'"""
        if (value in self.edges):
            self.regset.cfg_edg = self.edges[value]
        else:
            raise ValueError("Trigger edge should be one of {}".format(list(self.edges.keys())))

    @property
    def holdoff (self) -> int:
        """Trigger hold off time in clock periods"""
        return self.regset.cfg_hld

    @holdoff.setter
    def holdoff (self, value: int):
        """Trigger hold off time in clock periods"""
        # TODO: check range
        self.regset.cfg_hld = value

    @property
    def decimation (self) -> int:
        return (self.regset.cfg_dec + 1)

    @decimation.setter
    def decimation (self, value: int):
        # TODO check range
        self.regset.cfg_dec = value - 1

    @property
    def sample_rate (self) -> float:
        return (self.FS / self.decimation)

    @property
    def sample_period (self) -> float:
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
        return (bool(self.regset.cfg_byp))

    @filter_bypass.setter
    def filter_bypass (self, value: bool):
        if value:  self.regset.cfg_byp = 0x1
        else:      self.regset.cfg_mod = 0x0

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
        adr = cnt % self.N
        return adr

    def data(self, siz = N, ptr = None):
        """Data containing normalized values in the range [-1,1]"""
        if ptr is None:
            ptr = int(self.pointer)
        adr = (self.N + ptr - siz) % self.N
        # TODO: avoid making copy of entire array
        table = np.roll(self.table, -ptr)
        return table.astype('float32')[-siz:] * (self.__input_range / self.DWr)
