[Smart Alarmclock:]

Sets alarms automatically by looking at your calendar, detects if you're in
bed and makes sure you really get up. It has a very simple and extensible
plugin system which allows you to integrate it with different calendar
providers, your home theater system and even your home lighting system.


[Install on a Raspberry Pi:]

git clone https://github.com/dvc94ch/smartclock.git
cd smartclock
python setup.py sdist
sudo pip install dist/*.tar.gz
sudo echo "service smartclock start" >> /etc/rc.local
