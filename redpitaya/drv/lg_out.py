from ctypes import *
import numpy as np


class lg_out (object):
    """Logic generator output control.

    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | ``cfg_oen[0]`` | ``cfg_oen[1]`` | ``cfg_msk`` | ``cfg_val``    | **output**  |  **output**                   |
    |  out enable 0  |  out enable 1  |  out mask   | value/polarity | **enable**  | **equation**                  |
    +================+================+=============+================+=============+===============================+
    | 0              | 0              | x           | x              | Hi-Z        | ``z``                         |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | 0              | 1              | 0           |                | open drain  | ``          cfg_val ? 1 : z`` |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | 0              | 1              | 1           |                | open drain  | ``asg_val ^ cfg_val ? 1 : z`` |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | 1              | 0              | 0           |                | open source | ``          cfg_val ? z : 0`` |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | 1              | 0              | 1           |                | open source | ``asg_val ^ cfg_val ? z : 0`` |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | 1              | 1              | 0           |                | push-pull   | ``          cfg_val``         |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    | 1              | 1              | 1           |                | push-pull   | ``asg_val ^ cfg_val``         |
    +----------------+----------------+-------------+----------------+-------------+-------------------------------+
    """

    class _regset_t (Structure):
        _fields_ = [('cfg_oen', c_uint32 *2),  # output enable [0,1]
                    ('cfg_msk', c_uint32   ),  # mask
                    ('cfg_val', c_uint32   )]  # value/polarity

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.out.cfg_oen[0] = 0
        self.regset.out.cfg_oen[1] = 0
        self.regset.out.cfg_msk = 0
        self.regset.out.cfg_val = 0

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print(
            "cfg_oen[0] = 0x{reg:08x} = {reg:10d}  # output enable 0\n".format(reg=self.regset.out.cfg_oen[0]) +
            "cfg_oen[1] = 0x{reg:08x} = {reg:10d}  # output enable 1\n".format(reg=self.regset.out.cfg_oen[1]) +
            "cfg_msk    = 0x{reg:08x} = {reg:10d}  # output mask    \n".format(reg=self.regset.out.cfg_msk) +
            "cfg_val    = 0x{reg:08x} = {reg:10d}  # value/polarity \n".format(reg=self.regset.out.cfg_val)
        )

    @property
    def enable(self) -> _regset_t.cfg_oen:
        """Output enable [oe0, oe1]."""
        return self.regset.out.cfg_oen

    @enable.setter
    def enable(self, value: tuple):
        if isinstance(value, int):
            value = [value]*2
        self.regset.out.cfg_oen[0] = value[0]
        self.regset.out.cfg_oen[1] = value[1]

    @property
    def mask(self) -> int:
        """Output mask."""
        return self.regset.out.cfg_msk

    @mask.setter
    def mask(self, value: int):
        self.regset.out.cfg_msk = value

    @property
    def value(self) -> int:
        """Output value."""
        return self.regset.out.cfg_val

    @value.setter
    def value(self, value: int):
        self.regset.out.cfg_val = value
