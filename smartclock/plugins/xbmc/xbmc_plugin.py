"""
[Core]
Name = Xbmc Music Alarm Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Starts Xbmc and plays music.
"""


import logging
import urllib2
import socket

from smartclock.plugins.pluginlib import IAlarmPlugin

from smartclock.plugins.xbmc.xbmc import XBMC
from smartclock.plugins.xbmc.wakeonlan import wake_on_lan


class XbmcMusicAlarm(IAlarmPlugin):  # pragma: no cover
    """This Alarm starts playing a musicplaylist in xbmc."""

    default_settings = {
        'host': 'xbmc.craven.ch:8080',
        'username': 'xbmc',
        'password': 'xbmc',
        'mac': '00:01:2e:4b:d3:3a',
        'item': {
            'file': 'special://userdata/playlists/music/alarmclock.m3u'
        }
    }

    def activate(self):
        IAlarmPlugin.activate(self)
        self.url = "http://%s/jsonrpc" % self.settings['host']
        self.xbmc = XBMC(
            url=self.url, username=self.settings['username'],
            password=self.settings['password'])
        self.playback_started = False

    def _play(self):
        self._interval()

    def _interval(self):
        if not self.playback_started:
            try:
                self.xbmc.Player.Open({'item': self.settings['item']})
            except urllib2.URLError:
                wake_on_lan(self.settings['mac'])
                logging.getLogger(__name__).info(
                    "Request timed out, sending wol to %s."
                    % self.settings['mac'])
            except socket.timeout:
                pass
            else:
                self.playback_started = True
        else:
            self.xbmc.Application.SetVolume({'volume': 'increment'})

    def _pause(self):
        self.playback_started = False
