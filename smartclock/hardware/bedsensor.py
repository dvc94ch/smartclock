import os
import logging
import time
import threading

if os.name == 'nt':
    import msvcrt

from smartclock.hardware.device import Device


class Bedsensor(Device):

    BEDSENSOR = 22
    PRESSED = False
    RELEASED = True

    def __init__(self):
        Device.__init__(self, err="No bedsensor support, emulating bedsensor.")
        self.enabled = True
        if self.rpio is None:
            self.emulator_stop = threading.Event()
            self.emulator_thread = threading.Thread(
                target=self.emulator, args=(self.emulator_stop,))
            self.emulator_thread.start()
        else:  # pragma: no cover
            self.rpio.setup(
                self.BEDSENSOR, self.rpio.IN, pull_up_down=self.rpio.PUD_OFF)
            self.rpio.add_interrupt_callback(
                self.BEDSENSOR, self.isr, debounce_timeout_ms=100,
                threaded_callback=True)
            self.rpio.wait_for_interrupts(threaded=True)

        self.callbacks = []

        if self.rpio is None:
            self.state = self.PRESSED
        else:  # pragma: no cover
            self.state = self.read()

    def enable(self):
        self.enabled = True
        logging.getLogger(__name__).info("Enabled bedsensor.")

    def disable(self):
        self.enabled = False
        logging.getLogger(__name__).info(
            "Disabled bedsensor. Reading the bedsensor will return PRESSED.")

    def read(self):
        if self.enabled:
            if self.rpio is None:
                self.state = not self.state
            else:  # pragma: no cover
                self.state = self.rpio.input(self.BEDSENSOR)

            return self.state
        return self.PRESSED

    def isr(self, gpio_id, value):
        if not gpio_id == self.BEDSENSOR:
            return

        if value == self.PRESSED:  # pragma: no cover
            logging.getLogger(__name__).info(
                "Bed occupancy status changed to occupated.")
        else:
            logging.getLogger(__name__).info(
                "Bed occupancy status changed to unoccupated.")

        logging.getLogger(__name__).info("Calling callbacks.")

        if value:
            self.state = True
        else:
            self.state = False

        for callback in self.callbacks:
            callback(value)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def emulator(self, stop_event):
        logging.getLogger(__name__).info(
            "Bedsensor emulation thread is running.")
        if os.name == 'nt':
            while not stop_event.isSet():
                if msvcrt.kbhit():  # pragma: no cover
                    msvcrt.getch()
                    logging.getLogger(__name__).info(
                        "Received keyboard input.")
                    self.isr(self.BEDSENSOR, self.read())
                time.sleep(1)

        logging.getLogger(__name__).info("Stopped bedsensor emulation thread.")

    def get_state(self):
        if self.state == Bedsensor.PRESSED:
            return "PRESSED"
        return "RELEASED"

    def __del__(self):
        logging.info("Running destructor.")
        if self.rpio is None:
            self.emulator_stop.set()
        else:  # pragma: no cover
            Device.__del__(self)
