from redpitaya.drv.overlay import overlay

from periphery             import LED
from periphery             import GPIO

from redpitaya.drv.hwid    import hwid
from redpitaya.drv.mgmt    import mgmt
from redpitaya.drv.pdm     import pdm
from redpitaya.drv.clb     import clb
from redpitaya.drv.gen     import gen
from redpitaya.drv.osc     import osc
from redpitaya.drv.lg      import lg
from redpitaya.drv.la      import la

import iio


class mercury(overlay):

    def __init__(self):
        super().__init__(overlay='mercury')

    def __del__(self):
        super().__del__()

    # module number constants
    _MNG = 2  # generators
    _MNO = 2  # oscilloscopes

    _modules = tuple(['gen'+str(ch) for ch in range(_MNG)] + ['osc'+str(ch) for ch in range(_MNO)] + ['lg', 'la'])
    # TODO: it is unclear why the next line fails
    # sync_src = {event_sources[i]:      i for i in range(len(_modules))}
    # trig_src = {event_sources[i]: 1 << i for i in range(len(_modules))}
    sync_src = {'gen0': 0,
                'gen1': 1,
                'osc0': 2,
                'osc1': 3,
                'lg'  : 4,
                'la'  : 5}
    trig_src = {'gen0': 1 << 0,
                'gen1': 1 << 1,
                'osc0': 1 << 2,
                'osc1': 1 << 3,
                'lg'  : 1 << 4,
                'la'  : 1 << 5}

    class led(LED):
        leds = range(8)

        def __init__(self, index, brightness=None):
            if index not in self.leds:
                raise ValueError("LED index should be one of: {}".format(self.leds))
            else:
                super().__init__(name="led"+str(index), brightness=brightness)

    class gpio(GPIO):
        ports = {'p': 968, 'n': 976}
        gpios = range(8)

        def __init__(self, port, pin, direction="preserve"):
            if port not in self.ports:
                raise ValueError("GPIO port should be one of: {}".format(self.ports))
            if pin not in self.gpios:
                raise ValueError("GPIO pin should be one of: {}".format(self.gpios))
            else:
                super().__init__(pin=self.ports[port] + pin, direction=direction)

    class analog_in():
        channels = {0: 'vaux8', 1: 'vaux0', 2: 'vaux1', 3: 'vaux9'}
        ctx = iio.Context()
        # dev = ctx.devices[2] 
        # changes by explanation on https://forum.redpitaya.com/viewtopic.php?t=23485
        dev = ctx.find_device("iio:device1")
        # resistor divider
        resdiv = 4.99 / (30.0 + 4.99)

        def __init__(self, channel):
            if channel in range(4):
                channel = self.channels[channel]
            self.chn   = self.dev.find_channel(channel)
            self.scale = self.chn.attrs['scale'].value

        def read(self):
            raw = self.chn.attrs['raw'].value
            return (int(raw)*float(self.scale)/1000 / self.resdiv)

    class hwid(hwid):
        pass

    class mgmt(mgmt):
        pass

    class analog_out(pdm):
        V = 1.8  # voltage

        def read(self, ch: int) -> float:
            return (super().read(ch) / super().DWr * self.V)

        def write(self, ch: int, value: float):
            if (0 <= value <= self.V):
                super().write(ch, int(value / self.V * super()._DWr))
            else:
                raise ValueError("Output amplitude should be inside [0,{}] volts.".format(self.V))

    class clb(clb):
        # TODO, add checks
        pass

    class gen(gen):
        def __init__(self, index: int):
            if index in range(mercury._MNG):
                super().__init__(index=index)
                self.sync_src = mercury.sync_src['gen'+str(index)]
            else:
                raise ValueError("Generator index should be one of {}".format(range(mercury._MNG)))

    class osc(osc):
        def __init__(self, index: int, input_range: float):
            if index in range(mercury._MNO):
                super().__init__(index=index, input_range=input_range)
                self.sync_src = mercury.sync_src['osc'+str(index)]
                self.trig_src = mercury.trig_src['osc'+str(index)]
            else:
                raise ValueError("Oscilloscope index should be one of {}".format(range(mercury._MNO)))

    class lg(lg):
        def __init__(self):
            super().__init__()
            self.sync_src = mercury.sync_src['lg']

    class la(la):
        def __init__(self):
            super().__init__()
            self.sync_src = mercury.sync_src['la']
