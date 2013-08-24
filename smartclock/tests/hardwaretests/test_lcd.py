from unittest import TestCase

from smartclock.hardware.lcd import LCD


# Missing tests for update, display, _lcd_scroll.

class LcdTestCase(TestCase):

    def setUp(self):
        self.lcd = LCD()

    def test_backlight(self):
        self.assertTrue(
            self.lcd.backlight_value, "backlight should default to True.")
        self.lcd.backlight()
        self.assertEqual(
            self.lcd.backlight_value, False,
            "backlight should toggle if no value is supplied.")
        self.lcd.backlight(True)
        self.assertEqual(
            self.lcd.backlight_value, True, "backlight wasn't set to value.")

    def test_set_text(self):
        self.lcd.set_text("top line", "bottom line")
        self.assertEqual(
            (self.lcd.line_1, self.lcd.line_2), ("top line", "bottom line"),
            "set_text should set line_1 and line_2.")

    def tearDown(self):
        self.lcd.__del__()
