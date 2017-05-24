import numpy as np

from .uio import uio

class clb (uio):
    channels_adc = range(2)
    channels_dac = range(2)

    _MAGIC = 0xAABBCCDD
    _eeprom_device = "/sys/bus/i2c/devices/0-0050/eeprom"
    _eeprom_offset = 0x0008

    # FPGA regset structure
    _regset_channel_dtype = np.dtype([
        ('cfg_mul', 'int32'),  # multiplication
        ('cfg_sum', 'int32')   # summation
    ])
    _regset_dtype = np.dtype([
        ('dac', _regset_channel_dtype, 2),  # generator
        ('adc', _regset_channel_dtype, 2),  # oscilloscope
    ])

    # floating point structure
    _clb_channel_dtype = np.dtype([
        ('gain'  , 'float32'),  # multiplication
        ('offset', 'float32')   # summation
    ])
    _clb_range_dtype = np.dtype([
        ('lo', _clb_channel_dtype),  #  1.0V range
        ('hi', _clb_channel_dtype)   # 20.0V range
    ])
    clb_dtype = np.dtype([
        ('adc', _clb_range_dtype  , 2),  # oscilloscope
        ('dac', _clb_channel_dtype, 2),  # generator
    ])

    # EEPROM structure
    _eeprom_dtype = np.dtype([
        ('adc_hi_gain'  , 'uint32', 2),
        ('adc_lo_gain'  , 'uint32', 2),
        ('adc_lo_offset',  'int32', 2),
        ('dac_gain'     , 'uint32', 2),
        ('dac_offset'   ,  'int32', 2),
        ('magic'        , 'uint32'),
        ('adc_hi_offset',  'int32', 2)
    ])

    def __init__ (self, uio:str = '/dev/uio/clb'):
        super().__init__(uio)
        regset_array = np.recarray(1, self._regset_dtype, buf=self.uio_mmaps[0])
        self.regset = regset_array[0]

        self.adc = [self.ADC(self.regset.adc[ch]) for ch in self.channels_adc]
        self.dac = [self.DAC(self.regset.dac[ch]) for ch in self.channels_dac]

    def __del__ (self):
        super().__del__()

    class ADC (object):
        DW = 16
        _DWr = 2**DW - 1
        _DW1 = 2**(DW-2)

        def __init__ (self, regset):
            self.regset = regset

        @property
        def gain (self) -> float:
            """ADC gain calibration."""
            return (self.regset.cfg_mul / self._DW1)

        @gain.setter
        def gain (self, gain: float):
            self.regset.cfg_mul = int(gain * self._DW1)

        @property
        def offset (self) -> float:
            """ADC offset calibration."""
            return (self.regset.cfg_sum / self._DWr)

        @offset.setter
        def offset (self, offset: float):
            self.regset.cfg_mul = int(offset * self._DWr)

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
            self.regset.cfg_mul = int(offset * self._DWr)

    def eeprom_read (self):
        # open EEPROM device
        try:
            eeprom_file = open(self._eeprom_device, 'rb')
        except OSError as e:
            raise IOError(e.errno, "Opening {}: {}".format(uio, e.strerror))

        # seek to calibration data
        try:
            eeprom_file.seek(self._eeprom_offset)
        except IOError as e:
            raise IOError(e.errno, "Seek {}: {}".format(uio, e.strerror))

        try:
            buffer = eeprom_file.read (self._eeprom_dtype.itemsize)
        except IOError as e:
            raise IOError(e.errno, "Read {}: {}".format(uio, e.strerror))

        try:
            eeprom_file.close()
        except IOError as e:
            raise IOError(e.errno, "Close {}: {}".format(uio, e.strerror))

        # map buffer onto structure
        eeprom_array = np.recarray(1, self._eeprom_dtype, buf=buffer)
        eeprom_struct = eeprom_array[0]

        # missing magic number means a deprecated EEPROM structure was still not updated
        if (eeprom_struct.magic != self._MAGIC):
            for ch in self.channels_adc:
                eeprom_struct.adc_hi_off[ch] = eeprom_struct.adc_lo_off[ch];

        return (eeprom_struct)

    def FullScaleToVoltage(self, cnt: int) -> float:
        if cnt == 0:
            return (1.0)
        else:
            return (cnt * 100.0 / (1<<32))

    def FullScaleFromVoltage(self, voltage: float) -> int:
        return (int(voltage / 100.0 * (1<<32)));

    def eeprom_parse (eeprom_struct):

        # return structure
        clb_array = np.recarray(1, self._clb_dtype, buf=buffer)
        clb_struct = clb_array[0]

        # convert EEPROM values into local float values
        for ch in self.channels_adc:
            clb_struct.adc[ch].lo.gain   = self.FullScaleToVoltage (eeprom_struct.adc_lo_gain  [ch]) / 20.0
            clb_struct.adc[ch].hi.gain   = self.FullScaleToVoltage (eeprom_struct.adc_hi_gain  [ch])
            clb_struct.adc[ch].lo.offset =                          eeprom_struct.adc_lo_offset[ch]  / (2**13-1)
            clb_struct.adc[ch].hi.offset =                          eeprom_struct.adc_hi_offset[ch]  / (2**13-1) * 20.0
        for ch in self.channels_dac:
            clb_struct.dac[ch].gain      = self.FullScaleToVoltage (eeprom_struct.dac_gain     [ch])
            clb_struct.dac[ch].offset    =                          eeprom_struct.dac_offset   [ch]  / (2**13-1)

        return (clb_struct)

    def show_float (self, clb_struct):
        for ch in self.channels_adc:
            print('adc[{}].lo.gain   = {}'.format(ch, clb_struct.adc[ch].lo.gain))
            print('adc[{}].hi.gain   = {}'.format(ch, clb_struct.adc[ch].hi.gain))
            print('adc[{}].lo.offset = {}'.format(ch, clb_struct.adc[ch].lo.offset))
            print('adc[{}].hi.offset = {}'.format(ch, clb_struct.adc[ch].hi.offset))
        for ch in self.channels_dac:
            print('dac[{}].gain      = {}'.format(ch, clb_struct.dac[ch].gain))
            print('dac[{}].offset    = {}'.format(ch, clb_struct.dac[ch].offset))
