import numpy as np

from .uio import uio

class hwid (uio):
    """Driver for hardware identification module"""
    _regset_dtype = np.dtype([
        ('hwid' , 'uint32'),
        ('rsv0' , 'uint32'),  # reserved
        ('efuse', 'uint32'),
        ('rsv1' , 'uint32'),  # reserved
        ('dna'  , 'uint32', 2),
        ('rsv3' , 'uint32', 2),  # reserved
        ('gith' , 'uint32', 5)
    ])

    def __init__ (self, uio:str = '/dev/uio/hwid'):
        super().__init__(uio)
        regset_array = np.recarray(1, self._regset_dtype, buf=self.uio_mmaps[0])
        self.regset = regset_array[0]

    def __del__ (self):
        super().__del__()

    @property
    def hwid (self):
        """Red Pitaya hardware identification number (not very usefull)."""
        return (self.regset.hwid)

    @property
    def efuse (self):
        """Zynq FPGA efuse status."""
        return (self.regset.efuse)

    @property
    def dna (self):
        """Zynq FPGA DNA number."""
        return ((self.regset.dna[1] << 32) | self.regset.dna[0])

    @property
    def gith (self):
        """Git hash for the repository from which the FPGA was built."""
        return (''.join(["{:08x}".format(regid.regset.gith[i]) for i in range(5)]))
