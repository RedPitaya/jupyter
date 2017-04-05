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

    class pdm (pdm):
        # TODO, add checks
        pass

    class clb (clb):
        # TODO, add checks
        pass

    class gen (gen):
        # TODO, add checks
        pass

    class osc (osc):
        # TODO, add checks
        pass