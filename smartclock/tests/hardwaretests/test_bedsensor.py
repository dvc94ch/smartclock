from unittest import TestCase
from mock import MagicMock

from smartclock.hardware.bedsensor import Bedsensor


class TestBedsensor(TestCase):

    def setUp(self):
        self.bedsensor = Bedsensor()

    def test_enable_disable(self):
        self.bedsensor.disable()
        self.assertFalse(
            self.bedsensor.enabled, "disable didn't set enabled to false.")
        self.assertEquals(
            self.bedsensor.read(), self.bedsensor.PRESSED,
            "When the bedsensor ist disabled read should return PRESSED.")
        self.bedsensor.enable()
        self.assertTrue(
            self.bedsensor.enabled, "disable didn't set enabled to false.")

    def test_add_callback(self):
        cb_count = len(self.bedsensor.callbacks)
        self.bedsensor.add_callback(MagicMock())
        self.assertEquals(
            len(self.bedsensor.callbacks), cb_count + 1,
            "add_callback didn't increase callbacks size.")

    def test_read(self):
        if self.bedsensor.rpio is None:
            state = self.bedsensor.state
            self.assertNotEqual(
                self.bedsensor.read(), state,
                "read should change state in emulation mode.")

    def test_isr(self):
        callback = MagicMock()
        self.bedsensor.add_callback(callback)
        self.bedsensor.isr(self.bedsensor.BEDSENSOR, self.bedsensor.PRESSED)
        callback.assert_called_with(self.bedsensor.PRESSED)

    def tearDown(self):
        self.bedsensor.__del__()
