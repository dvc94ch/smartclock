[Smart Alarmclock:]

This is a smart alarmclock that allows integration with your calendar
software and home automation system through plugins. Plugins can collect
events automatically from calendars or manually by rules like MO-FR 8:00AM.
They can process events to modify travel_time, departure_time and reminder.
Also plugins can write to the lcd, implement custom alarms to integrate
with home cinema systems and register callbacks to the bedsensor to turn
the lights off when going to bed.


Install on a Raspberry Pi:

git clone ssh://git@git.craven.ch/~/smartclock.git
cd smartclock
python setup.py sdist
pip install dist/*.tar.gz
/etc/rc.local append "service smartclock start"
