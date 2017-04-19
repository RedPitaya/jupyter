import numpy as np

from .uio import uio

class pdm (uio):

    DN = 4
    DW = 8
    DWr = 2**DW - 1

    regset_dtype = np.dtype([
        ('pdm' , 'uint32', DN)
    ])

    def __init__ (self, uio:str = '/dev/uio/pdm'):
        super().__init__(uio)
        regset_array = np.recarray(1, self.regset_dtype, buf=self.uio_mmaps[0])
        self.regset = regset_array[0]

    def __del__ (self):
        super().__del__()

    def read (self, channel: int) -> int:
        return (self.regset.pdm[channel])

    def write (self, channel: int, value: int):
        if (value > self.DWr):
            raise ValueError("PDM output value should be in range [0,{}]".format(self.DWr))
        else:
            self.regset.pdm[channel] = value