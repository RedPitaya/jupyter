from ctypes import *

from .uio import uio


class mgmt(uio):
    """Driver for hardware identification module"""
    class _regset_t(Structure):
        _fields_ = [('cfg_iom' , c_uint32),  # GPIO mode (0 - PS GPIO, 1 - Logic generator)
                    ('cfg_loop', c_uint32)]  # enable internal digital loop from gen to osc

    def __init__(self, uio: str = '/dev/uio/mgmt'):
        super().__init__(uio)
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])

    def __del__(self):
        super().__del__()

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.cfg_iom = 0x0
        self.regset.cfg_loop = 0x0

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print(
            "cfg_iom  = 0x{reg:08x} = {reg:10d}  # GPIO mode    \n".format(reg = self.regset.cfg_iom) +
            "cfg_loop = 0x{reg:08x} = {reg:10d}  # gen->osc loop\n".format(reg = self.regset.cfg_loop)
        )

    @property
    def gpio_mode(self) -> int:
        """GPIO mode

        Each bit coresponds to one of {exp_n_io[7:0], exp_p_io[7:0]} GPIO pins.
        0 - pin is connected to PS GPIO controller
        1 - pin is connected to Logic generator.
        """
        return (self.regset.cfg_iom)

    @gpio_mode.setter
    def gpio_mode(self, value: int):
        self.regset.cfg_iom = value

    @property
    def loop(self) -> int:
        """Digital loopback (for debugging purposes)

        Each bit controls one of the loop paths:
        0 - enable loop: gen0 -> osc0,
        1 - enable loop: gen1 -> osc1.
        """
        return (self.regset.cfg_loop)

    @loop.setter
    def loop(self, value: int):
        self.regset.cfg_loop = value
