from redpitaya.drv.overlay import overlay

from periphery             import LED
from periphery             import GPIO

from redpitaya.drv.hwid    import hwid
from redpitaya.drv.pdm     import pdm
from redpitaya.drv.clb     import clb
from redpitaya.drv.gen     import gen
from redpitaya.drv.osc     import osc

class mercury (overlay):
    def __init__ (self):
        super().__init__ (overlay = 'mercury')

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