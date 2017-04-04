from periphery import GPIO

class gpio (GPIO):
    ports = {'p': 968, 'n': 976}
    def __init__ (self, port, pin, direction="preserve"):
        super().__init__ (pin = self.ports[port] + pin, direction = direction)
    