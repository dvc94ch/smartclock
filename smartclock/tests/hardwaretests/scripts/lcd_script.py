import logging
import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '../../../..'))
logging.basicConfig(filename='.log', level=logging.INFO)

from smartclock.hardware.lcd import LCD

lcd = LCD()

for i in range(15):
    lcd.set_text(line_1="*+*+*+*+*+*+*+*+", line_2="----------------")
    lcd.display()
    time.sleep(0.4)
