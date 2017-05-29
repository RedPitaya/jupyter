from ctypes import *

class osc_fil (object):
    # filter coeficients
    _filters = { 1.0: (0x7D93, 0x437C7, 0xd9999a, 0x2666),
                20.0: (0x4C5F, 0x2F38B, 0xd9999a, 0x2666)}

    class _regset_t (Structure):
        _fields_ = [('cfg_byp', c_uint32),  # bypass
                    ('cfg_faa',  c_int32),  # AA coeficient
                    ('cfg_fbb',  c_int32),  # BB coeficient
                    ('cfg_fkk',  c_int32),  # KK coeficient
                    ('cfg_fpp',  c_int32)]  # PP coeficient

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        print (
            "cfg_byp = 0x{reg:08x} = {reg:10d}  # bypass                    \n".format(reg=self.regset.fil.cfg_byp)+
            "cfg_faa = 0x{reg:08x} = {reg:10d}  # AA coeficient             \n".format(reg=self.regset.fil.cfg_faa)+
            "cfg_fbb = 0x{reg:08x} = {reg:10d}  # BB coeficient             \n".format(reg=self.regset.fil.cfg_fbb)+
            "cfg_fkk = 0x{reg:08x} = {reg:10d}  # KK coeficient             \n".format(reg=self.regset.fil.cfg_fkk)+
            "cfg_fpp = 0x{reg:08x} = {reg:10d}  # PP coeficient             \n".format(reg=self.regset.fil.cfg_fpp)
        )

    @property
    def filter_bypass (self) -> bool:
        """Bypass digital input filter.

        True   filter is not used
        False  filter is used
        """
        return (bool(self.regset.fil.cfg_byp))

    @filter_bypass.setter
    def filter_bypass (self, value: bool):
        self.regset.fil.cfg_byp = int(value)

    @property
    def filter_coeficients (self) -> tuple:
        return (self.regset.fil.cfg_faa,
                self.regset.fil.cfg_fbb,
                self.regset.fil.cfg_fkk,
                self.regset.fil.cfg_fpp)

    @filter_coeficients.setter
    def filter_coeficients (self, value: tuple):
        # TODO check range
        self.regset.fil.cfg_faa = value[0]
        self.regset.fil.cfg_fbb = value[1]
        self.regset.fil.cfg_fkk = value[2]
        self.regset.fil.cfg_fpp = value[3]