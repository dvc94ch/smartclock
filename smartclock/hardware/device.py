import logging


class Device(object):

    def __init__(self, err="ImportError, RPIO couldn't be imported."):
        try:
            self.rpio = __import__('RPIO')
        except ImportError:
            self.rpio = None
            logging.getLogger(__name__).info(err)

    def __del__(self):
        if self.rpio is not None:  # pragma: no cover
            self.rpio.cleanup()
