import logging
import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '../../../..'))
logging.basicConfig(filename='.log', level=logging.INFO)

from smartclock.hardware.lightsensor import Lightsensor

lightsensor = Lightsensor()
print lightsensor.read()
