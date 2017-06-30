from ctypes import *

from .uio import uio

class clb (uio):
    channels_dac = range(2)
    channels_adc = range(2)

    _MAGIC = 0xAABBCCDD
    _eeprom_device = "/sys/bus/i2c/devices/0-0050/eeprom"
    _eeprom_offset_user    = 0x0008
    _eeprom_offset_factory = 0x1c08

    # FPGA regset structure
    class _regset_t (Structure):
        class _regset_channel_t (Structure):
            _fields_ = [('cfg_mul', c_int32),  # multiplication
                        ('cfg_sum', c_int32)]  # summation
        _fields_ = [('dac', _regset_channel_t * 2),  # generator
                    ('adc', _regset_channel_t * 2)]  # oscilloscope

    # floating point structure
    class _clb_t (Structure):
        class _clb_range_t (Structure):
            class _clb_channel_t (Structure):
                _fields_ = [('gain'  , c_float),  # multiplication
                            ('offset', c_float)]  # summation
            _fields_ = [('lo', _clb_channel_t),  #  1.0V range
                        ('hi', _clb_channel_t)]  # 20.0V range
        _fields_ = [('dac', _clb_range_t._clb_channel_t * 2),  # generator
                    ('adc', _clb_range_t                * 2)]  # oscilloscope

    # EEPROM structure
    class _eeprom_t (Structure):
        _fields_ = [('adc_hi_gain'  , c_uint32 * 2),
                    ('adc_lo_gain'  , c_uint32 * 2),
                    ('adc_lo_offset',  c_int32 * 2),
                    ('dac_gain'     , c_uint32 * 2),
                    ('dac_offset'   ,  c_int32 * 2),
                    ('magic'        , c_uint32    ),
                    ('adc_hi_offset',  c_int32 * 2)]

    def __init__ (self, uio:str = '/dev/uio/clb'):
        super().__init__(uio)
        self.regset = self._regset_t.from_buffer(self.uio_mmaps[0])

        self.dac = [self.DAC(self.regset.dac[ch]) for ch in self.channels_dac]
        self.adc = [self.ADC(self.regset.adc[ch]) for ch in self.channels_adc]

    def __del__ (self):
        super().__del__()

    def show_regset(self):
        """Print FPGA module register set for debugging purposes."""
        for i in self.channels_dac:
            print (
                "cfg_mul = 0x{reg:08x} = {reg:10d}  # DAC[{i:d}] multiplication\n".format(reg=self.regset.dac[i].cfg_mul, i=i)+
                "cfg_sum = 0x{reg:08x} = {reg:10d}  # DAC[{i:d}] summation     \n".format(reg=self.regset.dac[i].cfg_sum, i=i)
            )
        for i in self.channels_adc:
            print (
                "cfg_mul = 0x{reg:08x} = {reg:10d}  # ADC[{i:d}] multiplication\n".format(reg=self.regset.adc[i].cfg_mul, i=i)+
                "cfg_sum = 0x{reg:08x} = {reg:10d}  # ADC[{i:d}] summation     \n".format(reg=self.regset.adc[i].cfg_sum, i=i)
            )

    class DAC (object):
        DW = 14
        _DWr = 2**DW - 1
        _DW1 = 2**(DW-2)

        def __init__ (self, regset):
            self.regset = regset

        @property
        def gain (self) -> float:
            """DAC gain calibration."""
            return (self.regset.cfg_mul / self._DW1)

        @gain.setter
        def gain (self, gain: float):
            self.regset.cfg_mul = int(gain * self._DW1)

        @property
        def offset (self) -> float:
            """DAC offset calibration."""
            return (self.regset.cfg_sum / self._DWr)

        @offset.setter
        def offset (self, offset: float):
            self.regset.cfg_sum = int(offset * self._DWr)

    class ADC (object):
        DW = 16
        _DWr = 2**DW - 1
        _DW1 = 2**(DW-2)

        def __init__ (self, regset):
            self.regset = regset

        @property
        def gain (self) -> float:
            """ADC gain calibration."""
            return (float(self.regset.cfg_mul) / self._DW1)

        @gain.setter
        def gain (self, gain: float):
            self.regset.cfg_mul = int(gain * self._DW1)

        @property
        def offset (self) -> float:
            """ADC offset calibration."""
            return (self.regset.cfg_sum / self._DWr)

        @offset.setter
        def offset (self, offset: float):
            self.regset.cfg_sum = int(offset * self._DWr)

    def eeprom_read (self, eeprom_offset = _eeprom_offset_user):
        # open EEPROM device
        try:
            eeprom_file = open(self._eeprom_device, 'rb')
        except OSError as e:
            raise IOError(e.errno, "Opening {}: {}".format(uio, e.strerror))

        # seek to calibration data
        try:
            eeprom_file.seek(eeprom_offset)
        except IOError as e:
            raise IOError(e.errno, "Seek {}: {}".format(uio, e.strerror))

        # read calibration data into a buffer
        try:
            buffer = eeprom_file.read (sizeof(self._eeprom_t))
        except IOError as e:
            raise IOError(e.errno, "Read {}: {}".format(uio, e.strerror))

        # close EEPROM device
        try:
            eeprom_file.close()
        except IOError as e:
            raise IOError(e.errno, "Close {}: {}".format(uio, e.strerror))

        # map buffer onto structure
        eeprom_struct = self._eeprom_t.from_buffer_copy(buffer)
        return (eeprom_struct)

    def FullScaleToVoltage(self, cnt: int) -> float:
        if cnt == 0:
            return (1.0)
        else:
            return (cnt * 100.0 / (1<<32))

    def FullScaleFromVoltage(self, voltage: float) -> int:
        return (int(voltage / 100.0 * (1<<32)));

    def eeprom_parse (self, eeprom_struct):

        # return structure
        clb_struct = self._clb_t()

        # convert EEPROM values into local float values
        for ch in self.channels_adc:
            if (eeprom_struct.magic == self._MAGIC):
                clb_struct.adc[ch].lo.gain = self.FullScaleToVoltage (eeprom_struct.adc_lo_gain  [ch]) / 20.0
                clb_struct.adc[ch].hi.gain = self.FullScaleToVoltage (eeprom_struct.adc_hi_gain  [ch])
            else:
                clb_struct.adc[ch].lo.gain = self.FullScaleToVoltage (eeprom_struct.adc_hi_gain  [ch])
                clb_struct.adc[ch].hi.gain = self.FullScaleToVoltage (eeprom_struct.adc_lo_gain  [ch]) / 20.0
            clb_struct.adc[ch].lo.offset   =                          eeprom_struct.adc_lo_offset[ch]  / (2**13-1)
            if (eeprom_struct.magic == self._MAGIC):
                clb_struct.adc[ch].hi.offset =                        eeprom_struct.adc_hi_offset[ch]  / (2**13-1) * 20.0
            else:
                clb_struct.adc[ch].hi.offset = clb_struct.adc[ch].lo.offset
        for ch in self.channels_dac:
            clb_struct.dac[ch].gain      = self.FullScaleToVoltage (eeprom_struct.dac_gain     [ch])
            clb_struct.dac[ch].offset    =                          eeprom_struct.dac_offset   [ch]  / (2**13-1)

        # missing magic number means a deprecated EEPROM structure was still not updated
        if (eeprom_struct.magic != self._MAGIC):
            for ch in self.channels_adc:
                clb_struct.adc[ch].hi.offset = clb_struct.adc[ch].lo.offset;

        return (clb_struct)

    def calib_show (self, clb_struct):
        for ch in self.channels_adc:
            print('adc[{}].lo.gain   = {}'.format(ch, clb_struct.adc[ch].lo.gain))
            print('adc[{}].hi.gain   = {}'.format(ch, clb_struct.adc[ch].hi.gain))
            print('adc[{}].lo.offset = {}'.format(ch, clb_struct.adc[ch].lo.offset))
            print('adc[{}].hi.offset = {}'.format(ch, clb_struct.adc[ch].hi.offset))
        for ch in self.channels_dac:
            print('dac[{}].gain      = {}'.format(ch, clb_struct.dac[ch].gain))
            print('dac[{}].offset    = {}'.format(ch, clb_struct.dac[ch].offset))

    def calib_apply (self, clb_struct, adc_range = ['lo', 'lo']):
        for ch in self.channels_adc:
            if   (adc_range[ch] == 'lo'):
                self.adc[ch].gain   = clb_struct.adc[ch].lo.gain
                self.adc[ch].offset = clb_struct.adc[ch].lo.offset
            elif (adc_range[ch] == 'hi'):
                self.adc[ch].gain   = clb_struct.adc[ch].hi.gain
                self.adc[ch].offset = clb_struct.adc[ch].hi.offset
            else:
                raise ValueError("ADC range can be one of ['lo', 'hi'].")
        for ch in self.channels_dac:
            self.dac[ch].gain   = clb_struct.dac[ch].gain
            self.dac[ch].offset = clb_struct.dac[ch].offset