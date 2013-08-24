import json
import urllib3

#host = 'xbmc'
host = 'test'

if host == 'xbmc':
    url = 'http://xbmc.craven.ch:8080/jsonrpc'
    file = 'special://userdata/playlists/music/alarmclock.m3u'
else:
    url = 'http://192.168.1.102:8080/jsonrpc'
    file = '/storage/emulated/0/Music/Avicii/Avicii/Avicii - Wake Me Up.mp3'

header = {
    'Content-Type': 'application/json'
}
jsonrpc = {
    'jsonrpc': '2.0',
    'method': 'Files.GetSources',
    'params': {
        'media': 'music'
    }
}
http = urllib3.PoolManager()
data = json.dumps(jsonrpc)
r = http.urlopen(method='POST', url=url, headers=header, body=data)
print r.status, r.data
