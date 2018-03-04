# CircuitPython_MCP23017
CircuitPython library for MCP23017 16-bit I/O expander.

## Example

```python
import board
import digitalio
import busio

from mcp23017 import *


i2c = busio.I2C(board.SCL, board.SDA)
expander = MCP23017(i2c)

led = expander.gpio(GPB0)
led.direction = digitalio.Direction.OUTPUT

switch = expander.gpio(GPA7)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

while True:
    if not switch.value:
        led.value = True
    else:
        led.value = False
```
