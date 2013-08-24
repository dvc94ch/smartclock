import logging
import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '../../../..'))
logging.basicConfig(filename='.log', level=logging.INFO)

from smartclock.hardware.bedsensor import Bedsensor

cb_called = False


def cb(state):
    global cb_called
    cb_called = True

bedsensor = Bedsensor()
bedsensor.add_callback(cb)

print "Current state: %s" % bedsensor.get_state()

print "Press key/bedsensor."

while cb_called is False:
    time.sleep(1)

print "Received state change: %s" % bedsensor.get_state()

bedsensor.__del__()
