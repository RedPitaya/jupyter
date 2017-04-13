from redpitaya.drv.overlay import overlay

from periphery             import LED
from periphery             import GPIO

from redpitaya.drv.hwid    import hwid
from redpitaya.drv.pdm     import pdm
from redpitaya.drv.clb     import clb
from redpitaya.drv.gen     import gen
from redpitaya.drv.osc     import osc

import iio

class mercury (overlay):
    
    def __init__ (self):
        super().__init__ (overlay = 'mercury')

    def __del__ (self):
        super().__del__ ()

    # module number constants
    MNG = 2  # generators
    MNO = 2  # oscilloscopes
    
    event_sources = tuple(['gen'+str(ch) for ch in range(MNG)] + ['osc'+str(ch) for ch in range(MNO)] + ['lg', 'la'])
    # TODO: it is unclear why the next line fails
    #event_masks = {event_sources[i]: 1<<i for i in range(len(event_sources))}
    event_masks = {'gen0': 0b000001,
                   'gen1': 0b000010,
                   'osc0': 0b000100,
                   'osc1': 0b001000,
                   'lg'  : 0b010000,
                   'la'  : 0b100000}
    # this functions are here just for some arguably user frendly redundancy
    sync_src = event_masks
    trig_src = event_masks

    class led (LED):
        leds = range(8)

        def __init__ (self, index, brightness=None):
            if index not in self.leds:
                raise ValueError("LED index should be one of: {}".format(self.leds))
            else:
                super().__init__ (name = "led"+str(index), brightness = brightness)

    class gpio (GPIO):
        ports = {'p': 968, 'n': 976}
        gpios = range(8)

        def __init__ (self, port, pin, direction="preserve"):
            if port not in self.ports:
                raise ValueError("GPIO port should be one of: {}".format(self.ports))
            if pin not in self.gpios:
                raise ValueError("GPIO pin should be one of: {}".format(self.gpios))
            else:
                super().__init__ (pin = self.ports[port] + pin, direction = direction)

    class analog_in ():
        channels = {0:'vaux8', 1:'vaux0', 2:'vaux1', 3:'vaux9'}
        ctx = iio.Context()
        dev = ctx.devices[3]
        # resistor divider
        resdiv = 4.99 / (30.0 + 4.99)

        def __init__ (self, channel):
            if channel in range(4):
                channel = self.channels[channel]
            self.chn   = self.dev.find_channel(channel)
            self.scale = self.chn.attrs['scale'].value

        def read(self):
            raw = self.chn.attrs['raw'].value
            return (int(raw)*float(self.scale)/1000 / self.resdiv)

    class hwid (hwid):
        pass

    class analog_out (pdm):
        V = 1.8  # voltage

        def read (self, ch: int) -> float:
            return (super().read(ch) / super().DWr * self.V)

        def write (self, ch: int, value: float):
            super().write(ch, value / self.V * super().DWr)

    class clb (clb):
        # TODO, add checks
        pass

    class gen (gen):
        def __init__ (self, index:int):
            if index in range(mercury.MNG):
                super().__init__ (index = index)
                self.sync_src = mercury.event_masks['gen'+str(index)]
            else:
                raise ValueError("Generator index should be one of {}".format(range(mercury.MNG)))

    class osc (osc):
        def __init__ (self, index:int, input_range:float):
            if index in range(mercury.MNO):
                super().__init__ (index = index, input_range = input_range)
                self.sync_src = mercury.event_masks['osc'+str(index)]
                self.trig_src = mercury.event_masks['osc'+str(index)]
            else:
                raise ValueError("Oscilloscope index should be one of {}".format(range(mercury.MNO)))
