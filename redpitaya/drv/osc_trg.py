from ctypes import *


class osc_trg(object):
    # trigger edge dictionary
    _edges = {'pos': 0, 'neg': 1}

    class _regset_t(Structure):
        _fields_ = [('cfg_neg',  c_int32),  # negative level
                    ('cfg_pos',  c_int32),  # positive level
                    ('cfg_edg', c_uint32)]  # edge (0-pos, 1-neg)

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.trg.cfg_neg = 0
        self.regset.trg.cfg_pos = 0
        self.regset.trg.cfg_edg = 0

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print(
            "cfg_neg = 0x{reg:08x} = {reg:10d}  # negative level     \n".format(reg=self.regset.trg.cfg_neg) +
            "cfg_pos = 0x{reg:08x} = {reg:10d}  # positive level     \n".format(reg=self.regset.trg.cfg_pos) +
            "cfg_edg = 0x{reg:08x} = {reg:10d}  # edge (0-pos, 1-neg)\n".format(reg=self.regset.trg.cfg_edg) +
        )

    @property
    def level(self) -> float:
        """Trigger level in vols, or a pair of values [neg, pos] if a hysteresis is desired."""
        scale = self.input_range / self._DWr
        return [self.regset.trg.cfg_neg * scale, self.regset.trg.cfg_pos * scale]

    @level.setter
    def level(self, value: tuple):
        scale = self._DWr / self.input_range
        if isinstance(value, float):
            value = [value]*2
        if (-1.0 <= value[0] <= 1.0):
            self.regset.trg.cfg_neg = int(value[0] * scale)
        else:
            raise ValueError("Trigger negative level should be inside [{},{}]".format(self.input_range))
        if (-1.0 <= value[1] <= 1.0):
            self.regset.trg.cfg_pos = int(value[1] * scale)
        else:
            raise ValueError("Trigger positive level should be inside [{},{}]".format(self.input_range))

    @property
    def edge(self) -> str:
        """Trigger edge as a string 'pos'/'neg'"""
        return ('pos', 'neg')[self.regset.trg.cfg_edg]

    @edge.setter
    def edge(self, value: str):
        if (value in self._edges):
            self.regset.trg.cfg_edg = self._edges[value]
        else:
            raise ValueError("Trigger edge should be one of {}".format(list(self._edges.keys())))
