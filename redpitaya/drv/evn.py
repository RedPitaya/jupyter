from ctypes import *

class evn ():
    # control register masks
    _CTL_TRG_MASK = 1<<3  # sw trigger bit (sw trigger must be enabled)
    _CTL_STP_MASK = 1<<2  # stop/abort; returns 1 when stopped
    _CTL_STR_MASK = 1<<1  # start
    _CTL_RST_MASK = 1<<0  # reset state machine so that it is in known state

    class _regset_t (Structure):
        _fields_ = [('ctl_sts', c_uint32),  # control/status register
                    ('cfg_evn', c_uint32),  # software event source select
                    ('cfg_trg', c_uint32)]  # hardware trigger mask

    def show_regset (self):
        """Print FPGA module register set for debugging purposes."""
        print (
            "ctl_sts = 0x{reg:08x} = {reg:10d}  # control/status            \n".format(reg=self.regset.evn.ctl_sts)+
            "cfg_evn = 0x{reg:08x} = {reg:10d}  # SW event source select    \n".format(reg=self.regset.evn.cfg_evn)+
            "cfg_trg = 0x{reg:08x} = {reg:10d}  # HW trigger mask           \n".format(reg=self.regset.evn.cfg_trg)
        )

    def reset (self):
        """Reset state machine, is used to synchronize alwways running streams."""
        self.regset.evn.ctl_sts = self._CTL_RST_MASK

    def start (self):
        """Start starte machine."""
        self.regset.evn.ctl_sts = self._CTL_STR_MASK

    def stop (self):
        """Stop state machine."""
        self.regset.evn.ctl_sts = self._CTL_STP_MASK

    def trigger (self):
        """Activate SW trigger."""
        self.regset.evn.ctl_sts = self._CTL_TRG_MASK

    def status_run (self) -> bool:
        """Run status."""
        return (bool(self.regset.evn.ctl_sts & self._CTL_STR_MASK))

    def status_trigger (self) -> bool:
        """Trigger status."""
        return (bool(self.regset.evn.ctl_sts & self._CTL_TRG_MASK))

    @property
    def sync_src (self) -> int:
        """Select for software event sources."""
        return (self.regset.evn.cfg_evn)

    @sync_src.setter
    def sync_src (self, value: int):
        self.regset.evn.cfg_evn = value

    @property
    def trig_src (self) -> int:
        """Enable mask for hardware trigger sources."""
        return (self.regset.evn.cfg_trg)

    @trig_src.setter
    def trig_src (self, value: int):
        self.regset.evn.cfg_trg = value
