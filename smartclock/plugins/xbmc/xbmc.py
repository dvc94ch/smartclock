import logging
import urllib2
import json

PLAYER_MUSIC = 0
PLAYER_VIDEO = 1


class XBMCTransport(object):

    def execute(self, method, args):
        pass


class XBMCJsonTransport(XBMCTransport):

    def __init__(self, url, username='xbmc', password='xbmc'):
        self.url = url
        self.username = username
        self.password = password

    def execute(self, method, *args, **kwargs):
        header = {
            'Content-Type': 'application/json'
        }
        if len(args) == 1:
            args = args[0]
        params = kwargs
        params['jsonrpc'] = '2.0'
        params['method'] = method
        params['params'] = args

        values = json.dumps(params)

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm=None, uri=self.url, user=self.username, passwd=self.password)
        opener = urllib2.build_opener(auth_handler)
        # ...and install it globally so it can be used with urlopen.
        urllib2.install_opener(opener)
        data = values
        req = urllib2.Request(self.url, data, header)
        logging.getLogger(__name__).info(
            "url: %s, data: %s" % (req.get_full_url(), req.get_data()))
        response = urllib2.urlopen(req, timeout=1).read()
        logging.getLogger(__name__).info(response)
        return response


class XBMC(object):

    def __init__(self, url, username='xbmc', password='xbmc'):
        self.transport = XBMCJsonTransport(url, username, password)
        # pylint: disable-msg=invalid-name
        self.VideoLibrary = VideoLibrary(self.transport)
        self.Application = Application(self.transport)
        self.Gui = Gui(self.transport)
        self.Player = Player(self.transport)
        self.Playlist = Playlist(self.transport)

    def execute(self, *args, **kwargs):
        self.transport.execute(*args, **kwargs)


class XbmcNamespace(object):

    def __init__(self, xbmc):
        self.xbmc = xbmc

    def __getattr__(self, name):
        class_ = self.__class__.__name__
        method = name
        xbmcmethod = "%s.%s" % (class_, method)

        def hook(*args, **kwargs):
            return self.xbmc.execute(xbmcmethod, *args, **kwargs)

        return hook


class VideoLibrary(XbmcNamespace):
    pass


class Application(XbmcNamespace):
    pass


class Gui(XbmcNamespace):
    pass


class Player(XbmcNamespace):
    pass


class Playlist(XbmcNamespace):
    pass
