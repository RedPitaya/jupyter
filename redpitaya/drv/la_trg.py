from ctypes import *


class la_trg(object):
    class _regset_t(Structure):
        _fields_ = [('cfg_cmp_msk', c_uint32),  # comparator mask
                    ('cfg_cmp_val', c_uint32),  # comparator value
                    ('cfg_edg_pos', c_uint32),  # edge positive
                    ('cfg_edg_neg', c_uint32)]  # edge negative

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        print(
            "cfg_cmp_msk = 0x{reg:08x} = {reg:10d}  # comparator mask \n".format(reg = self.regset.trg.cfg_cmp_msk) +
            "cfg_cmp_val = 0x{reg:08x} = {reg:10d}  # comparator value\n".format(reg = self.regset.trg.cfg_cmp_val) +
            "cfg_edg_pos = 0x{reg:08x} = {reg:10d}  # edge positive   \n".format(reg = self.regset.trg.cfg_edg_pos) +
            "cfg_edg_neg = 0x{reg:08x} = {reg:10d}  # edge negative   \n".format(reg = self.regset.trg.cfg_edg_neg)
        )

    def default(self):
        """Set registers into default (power-up) state."""
        self.regset.trg.cfg_cmp_msk = 0
        self.regset.trg.cfg_cmp_val = 0
        self.regset.trg.cfg_edg_pos = 0
        self.regset.trg.cfg_edg_neg = 0

    @property
    def trigger_mask(self) -> int:
        """Trigger comparator mask."""
        return (self.regset.trg.cfg_cmp_msk)

    @trigger_mask.setter
    def trigger_mask(self, value: tuple):
        self.regset.trg.cfg_cmp_msk = value

    @property
    def trigger_value(self) -> int:
        """Trigger comparator value."""
        return (self.regset.trg.cfg_cmp_val)

    @trigger_value.setter
    def trigger_value(self, value: tuple):
        self.regset.trg.cfg_cmp_val = value

    @property
    def trigger_edge(self) -> tuple:
        """Trigger edge detection mask [pos, neg]."""
        return ([self.regset.trg.cfg_edg_pos, self.regset.trg.cfg_edg_neg])

    @trigger_edge.setter
    def trigger_edge(self, value: tuple):
        [self.regset.trg.cfg_edg_pos, self.regset.trg.cfg_edg_neg] = value
