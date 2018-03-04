import digitalio


GPA0 = (0x12, 0x00, 0x0c, 0x14, 0)
GPA1 = (0x12, 0x00, 0x0c, 0x14, 1)
GPA2 = (0x12, 0x00, 0x0c, 0x14, 2)
GPA3 = (0x12, 0x00, 0x0c, 0x14, 3)
GPA4 = (0x12, 0x00, 0x0c, 0x14, 4)
GPA5 = (0x12, 0x00, 0x0c, 0x14, 5)
GPA6 = (0x12, 0x00, 0x0c, 0x14, 6)
GPA7 = (0x12, 0x00, 0x0c, 0x14, 7)

GPB0 = (0x13, 0x01, 0x0d, 0x15, 0)
GPB1 = (0x13, 0x01, 0x0d, 0x15, 1)
GPB2 = (0x13, 0x01, 0x0d, 0x15, 2)
GPB3 = (0x13, 0x01, 0x0d, 0x15, 3)
GPB4 = (0x13, 0x01, 0x0d, 0x15, 4)
GPB5 = (0x13, 0x01, 0x0d, 0x15, 5)
GPB6 = (0x13, 0x01, 0x0d, 0x15, 6)
GPB7 = (0x13, 0x01, 0x0d, 0x15, 7)


class Port:
    def __init__(self, device, gpio_address, iodir_address, gppu_address,
                 olat_address, position):
        self.gpio_address = gpio_address
        self.iodir_address = iodir_address
        self.gppu_address = gppu_address
        self.olat_address = olat_address
        self.position = position
        self.device = device

    def _get(self, register_address):
        v = self.device._read(register_address)
        v = v >> self.position
        v &= 1
        if v:
            return True
        else:
            return False

    def _set(self, register_address, val):
        v = self.device._read(register_address)
        if val:
            v |= 1 << self.position
        else:
            v &= ~(1 << self.position)
        self.device._write(register_address, v)

    @property
    def value(self):
        return self._get(self.gpio_address)

    @value.setter
    def value(self, val):
        if self.direction is digitalio.Direction.INPUT:
            raise AttributeError("Cannot set value when direction is input.")
        self._set(self.olat_address, val)

    @property
    def direction(self):
        if self._get(self.iodir_address):
            return digitalio.Direction.INPUT
        else:
            return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self, direction):
        if direction is digitalio.Direction.INPUT:
            self._set(self.iodir_address, True)
        elif direction is digitalio.Direction.OUTPUT:
            self._set(self.iodir_address, False)
        else:
            raise ValueError("Invalid direction.")

    @property
    def pull(self):
        if self._get(self.gppu_address):
            return digitalio.Pull.UP
        else:
            return None

    @pull.setter
    def pull(self, pullup):
        if pullup is digitalio.Pull.UP:
            self._set(self.gppu_address, True)
        elif pullup is None:
            self._set(self.gppu_address, False)
        else:
            raise ValueError("Unsupported pull value.")


class MCP23017:
    """Interface to the MCP23017 I/O expander."""

    _BUFFER = bytearray(2)

    def __init__(self, i2c, address=0x20):
        self._i2c = i2c
        self._address = address

    def _write(self, register_address, value):
        try:
            while not self._i2c.try_lock():
                pass
            self._BUFFER[0] = register_address
            self._BUFFER[1] = value
            self._i2c.writeto(self._address, self._BUFFER)
        finally:
            self._i2c.unlock()

    def _read(self, register_address):
        try:
            while not self._i2c.try_lock():
                pass
            self._BUFFER[0] = register_address
            self._i2c.writeto(self._address, self._BUFFER, end=1, stop=False)
            self._i2c.readfrom_into(self._address, self._BUFFER, start=1)
            return self._BUFFER[1]
        finally:
            self._i2c.unlock()

    def gpio(self, pin):
        return Port(self, *pin)
