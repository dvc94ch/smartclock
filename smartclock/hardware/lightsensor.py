import time

from smartclock.hardware.device import Device


class Lightsensor(Device):

    LIGHTSENSOR = 24

    def __init__(self):
        Device.__init__(self, err="No Lightsensor support.")

    def read(self):  # pragma: no cover
        """Measures time for capacitor to charge."""

        if self.rpio is None:
            return 0

        measurement = 0
        # Discarge capacitor.
        self.rpio.setup(self.LIGHTSENSOR, self.rpio.OUT)
        self.rpio.output(self.LIGHTSENSOR, self.rpio.LOW)
        time.sleep(0.1)

        self.rpio.setup(self.LIGHTSENSOR, self.rpio.IN)
        # Count loops until voltage across capacitor reads high.
        while (self.rpio.input(self.LIGHTSENSOR) == self.rpio.LOW):
            measurement += 1

        return measurement
