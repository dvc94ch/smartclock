import os
import platform
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install as _install


class install(_install):
    def run(self):
        _install.run(self)
        os.chmod('/etc/init.d/smartclock', 755)
        os.chmod(
            '/usr/local/lib/python2.7/dist-packages/smartclock/main.py', 755)


setup(
    name='SmartClock',
    version='0.1.0',
    description='''Sets alarms automatically by looking at your calendar,
                detects if you're in bed and makes sure you really get up.''',
    author='David Craven',
    author_email='david@craven.ch',
    url='craven.ch',
    license=open('smartclock/LICENSE.txt').read(),
    packages=find_packages(),
    package_data={'': ['*.txt', '*.md']},
    long_description=open('smartclock/README.md').read(),
    install_requires=[
        'apscheduler', 'gdata', 'geopy', 'python-daemon', 'rpio', 'yapsy'],
    data_files=[('/etc/init.d', ['smartclock/system/smartclock']),
                ('/etc/default', ['smartclock/system/watchdog']),
                ('/etc', ['smartclock/system/watchdog.conf'])],
    cmdclass={'install': install}
)
