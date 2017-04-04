import numpy as np

from .uio import uio

class pdm ():

    DN = 4
    DW = 8
    DWr = 2**DW
    V = 1.8  # voltage

    regset_dtype = np.dtype([
        ('pdm' , 'uint32', DN)
    ])

    def __init__ (self, uio:str = '/dev/uio/pdm'):
        super().__init__(uio)

    def __del__ (self):
        super().__del__()

    @property
    def pdm (self) -> tuple:
        return ([self.regset.pdm[i] / self.DWr * self.V for i in range(self.DN)])

    @pdm.setter
    def pdm (self, value: tuple):
         for i in range(self.DN):
             self.regset.pdm[i] = value[i] / self.V * self.DWr
