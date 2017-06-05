from ctypes import *

from .uio import uio

class mgmt (uio):
    """Driver for hardware identification module"""
    class _regset_t (Structure):
         _fields_ = [('cfg_iom', c_uint32)]

    def __init__ (self, uio:str = '/dev/uio/mgmt'):
        super().__init__(uio)
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])

    def __del__ (self):
        super().__del__()

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        print (
            "cfg_iom = 0x{reg:08x} = {reg:10d}  # GPIO mode\n".format(reg=self.regset.cfg_iom)
        )

    @property
    def gpio_mode (self) -> int:
        """GPIO mode
        
        Each bit coresponds to one of {exp_n_io[7:0], exp_p_io[7:0]} GPIO pins.
        0 - pin is connected to PS GPIO controller
        1 - pin is connected to Logic generator.
        """
        return (self.regset.cfg_iom)

    @gpio_mode.setter
    def gpio_mode (self, value: int):
        self.regset.cfg_iom = value