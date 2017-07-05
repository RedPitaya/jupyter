from ctypes import *

from .uio import uio


class hwid(uio):
    """Driver for hardware identification module.

    Attributes
    ----------
    hwid : int
        Red Pitaya FPGA identification number (32bit).
    efuse : int
        Zynq FPGA efuse (57bit).
    dna : int
        Zynq FPGA DNA number (57bit).
    gith : str
        Git hash (160 bits, 40 hex characters)

    .. note::

        Future releases might provide access to other Zynq FPGA features.
    """
    class _regset_t(Structure):
        _fields_ = [('hwid' , c_uint32    ),
                    ('rsv0' , c_uint32    ),  # reserved
                    ('efuse', c_uint32    ),
                    ('rsv1' , c_uint32    ),  # reserved
                    ('dna'  , c_uint32 * 2),
                    ('rsv3' , c_uint32 * 2),  # reserved
                    ('gith' , c_uint32 * 5)]

    def __init__(self, uio: str = '/dev/uio/hwid'):
        super().__init__(uio)
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])

    def __del__(self):
        super().__del__()

    @property
    def hwid(self) -> int:
        """Red Pitaya FPGA identification number.

        A 32bit read only register defined at FPGA compile time.
        """
        return (self.regset.hwid)

    @property
    def efuse(self) -> int:
        """Zynq FPGA efuse.

        A 32bit value, read only for now, future versions might provide a convoluted write access scheme.
        """
        return (self.regset.efuse)

    @property
    def dna(self) -> int:
        """Zynq FPGA DNA number.

        A 57bit read-only value defined in manufacturing.
        Can be used as an almost unique device identification.
        """
        return ((self.regset.dna[1] << 32) | self.regset.dna[0])

    @property
    def gith(self) -> str:
        """Git hash.

        A full SHA-1 hash (160 bits, 40 hex characters)
        for the repository from which the FPGA was built.
        """
        return (''.join(["{:08x}".format(self.regset.gith[i]) for i in range(5)]))
