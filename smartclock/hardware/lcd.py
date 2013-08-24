import os
import time
from collections import deque

from smartclock.hardware.device import Device


class LCD(Device):

    # Define GPIO to LCD mapping
    LCD_RS = 14
    LCD_E = 18
    LCD_D4 = 2
    LCD_D5 = 3
    LCD_D6 = 4
    LCD_D7 = 17
    LCD_LED = 27

    # Define some device constants
    LCD_WIDTH = 16    # Maximum characters per line
    LCD_CHR = True
    LCD_CMD = False

    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

    # Timing constants
    E_PULSE = 0.00005
    E_DELAY = 0.00005

    line_1 = ""
    line_2 = ""
    lcd_text_1_queue = deque()
    lcd_text_2_queue = deque()

    backlight_value = True

    def __init__(self, backlight=True):
        Device.__init__(self, err="No LCD support, emulating LCD.")
        if self.rpio is not None:  # pragma: no cover
            self._gpio_init()
            self._lcd_init()

        self.backlight(backlight)

    def backlight(self, value=None):
        if value is None:
            self.backlight_value = not self.backlight_value
        else:
            self.backlight_value = value

        if self.rpio is not None:  # pragma: no cover
            self.rpio.output(self.LCD_LED, self.backlight_value)

    def set_text(self, line_1, line_2=""):
        self.line_1 = line_1
        self.line_2 = line_2

    def update(self, lcd_line=0x00):
        if lcd_line == 0x00 or lcd_line == self.LCD_LINE_1:
            if len(self.line_1) > 16:
                for lcd_text in self._lcd_scroll(self.line_1):
                    self.lcd_text_1_queue.append(lcd_text)
            else:
                self.lcd_text_1_queue.append(self.line_1)

        if lcd_line == 0x00 or lcd_line == self.LCD_LINE_2:
            if len(self.line_2) > 16:
                for lcd_text in self._lcd_scroll(self.line_2):
                    self.lcd_text_2_queue.append(lcd_text)
            else:
                self.lcd_text_2_queue.append(self.line_2)

    def display(self):
        if not self.lcd_text_1_queue:
            self.update(self.LCD_LINE_1)

        if not self.lcd_text_2_queue:
            self.update(self.LCD_LINE_2)

        line_1 = self.lcd_text_1_queue.popleft()
        line_2 = self.lcd_text_2_queue.popleft()
        if self.rpio is not None:  # pragma: no cover
            self._lcd_byte(self.LCD_LINE_1, self.LCD_CMD)
            self._lcd_string(line_1)

            self._lcd_byte(self.LCD_LINE_2, self.LCD_CMD)
            self._lcd_string(line_2)
        else:
            self._print(line_1, line_2)

    def _lcd_scroll(self, message):
        str_pad = " " * 16
        message = str_pad + message
        for i in range(0, len(message)):
            yield message[i:(i + 15)]
        yield str_pad

    def _print(self, line_1, line_2):  # pragma: no cover
        os.system('cls' if os.name == 'nt' else 'clear')
        if self.backlight_value:
            print line_1
            print line_2

    def _gpio_init(self):  # pragma: no cover

        self.rpio.setwarnings(False)
        self.rpio.setup(self.LCD_E, self.rpio.OUT)  # E
        self.rpio.setup(self.LCD_RS, self.rpio.OUT)  # RS
        self.rpio.setup(self.LCD_D4, self.rpio.OUT)  # DB4
        self.rpio.setup(self.LCD_D5, self.rpio.OUT)  # DB5
        self.rpio.setup(self.LCD_D6, self.rpio.OUT)  # DB6
        self.rpio.setup(self.LCD_D7, self.rpio.OUT)  # DB7
        self.rpio.setup(self.LCD_LED, self.rpio.OUT)  # Backlight

    def _lcd_init(self):  # pragma: no cover

        # Initialise display
        self._lcd_byte(0x33, self.LCD_CMD)
        self._lcd_byte(0x32, self.LCD_CMD)
        self._lcd_byte(0x28, self.LCD_CMD)
        self._lcd_byte(0x0C, self.LCD_CMD)
        self._lcd_byte(0x06, self.LCD_CMD)
        self._lcd_byte(0x01, self.LCD_CMD)

    def _lcd_string(self, message):  # pragma: no cover
        # Send string to display

        message = message.ljust(self.LCD_WIDTH, " ")

        for i in range(self.LCD_WIDTH):
            self._lcd_byte(ord(message[i]), self.LCD_CHR)

    def _lcd_byte(self, bits, mode):  # pragma: no cover
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command

        self.rpio.output(self.LCD_RS, mode)  # RS

        # High bits
        self.rpio.output(self.LCD_D4, False)
        self.rpio.output(self.LCD_D5, False)
        self.rpio.output(self.LCD_D6, False)
        self.rpio.output(self.LCD_D7, False)
        if bits & 0x10 == 0x10:
            self.rpio.output(self.LCD_D4, True)
        if bits & 0x20 == 0x20:
            self.rpio.output(self.LCD_D5, True)
        if bits & 0x40 == 0x40:
            self.rpio.output(self.LCD_D6, True)
        if bits & 0x80 == 0x80:
            self.rpio.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        time.sleep(self.E_DELAY)
        self.rpio.output(self.LCD_E, True)
        time.sleep(self.E_PULSE)
        self.rpio.output(self.LCD_E, False)
        time.sleep(self.E_DELAY)

        # Low bits
        self.rpio.output(self.LCD_D4, False)
        self.rpio.output(self.LCD_D5, False)
        self.rpio.output(self.LCD_D6, False)
        self.rpio.output(self.LCD_D7, False)
        if bits & 0x01 == 0x01:
            self.rpio.output(self.LCD_D4, True)
        if bits & 0x02 == 0x02:
            self.rpio.output(self.LCD_D5, True)
        if bits & 0x04 == 0x04:
            self.rpio.output(self.LCD_D6, True)
        if bits & 0x08 == 0x08:
            self.rpio.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        time.sleep(self.E_DELAY)
        self.rpio.output(self.LCD_E, True)
        time.sleep(self.E_PULSE)
        self.rpio.output(self.LCD_E, False)
        time.sleep(self.E_DELAY)
