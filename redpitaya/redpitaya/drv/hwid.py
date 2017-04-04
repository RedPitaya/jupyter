import numpy as np

from .uio import uio

class hwid (uio):
    regset_dtype = np.dtype([
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

    def __del__ (self):
        super().__del__()

    @property
    def hwid (self):
        return (self.regset.hwid)

    @property
    def efuse (self):
        return (self.regset.efuse)

    @property
    def dna (self):
        return ((self.regset.dna[1] << 32) | self.regset.dna[0])

    @property
    def gith (self):
        return (''.join(["{:08x}".format(regid.regset.gith[i]) for i in range(5)]))
