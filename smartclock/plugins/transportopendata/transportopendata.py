import json
import logging
import urllib
import urllib2


class Location(object):
    """ id: The id of the location
        name: The location name
        score: The accuracy of the result
        coordinates: The location coordinates
        distance: If search has been with coordinates, distance to original
                  point in meters
    """

    def __init__(self, kwargs):
        self.uid = kwargs['id']
        self.name = kwargs['name']
        self.score = kwargs['score']
        self.coordinates = Coordinates(kwargs['coordinate'])
        self.distance = kwargs.get('distance', None)


class Coordinates(object):
    """ type: The type of the given coordinate.
        x: Latitude.
        y: Longitude.
    """

    def __init__(self, kwargs):
        self.latitude = kwargs['x']
        self.longitude = kwargs['y']
        self.type = kwargs['type']


class TransportOpendata(object):

    def get_locations(self, query, **kwargs):
        """ query: Specifies the location name to search for.
                   Example: Basel
            x: Latitude. Example: 47.476001
            y: Longitude. Example: 8.306130
            type: Specifies the location type, possible types are:
                    all (default): Looks up for all types of locations
                    station: Looks up for stations (train station, bus station)
                    poi: Looks up for points of interest (Clock tower, China
                         garden)
                    address: Looks up for an address (Zurich Bahnhofstrasse 33)
        """

        url = "http://transport.opendata.ch/v1/locations"

        kwargs['query'] = query

        response = self.http_get(url, kwargs)

        return [Location(loc) for loc in response['stations']]

    def get_connections(self, origin, destination, **kwargs):
        """ from: Specifies the departure location of the connection.
                  Example: Lausanne
            to: Specifies the arrival location of the connection.
                Example: Geneve
            via: Specifies up to five via locations. When specifying several
                 vias, array notation (via[]=via1&via[]=via2) is required.
                 Example: Bern
            date: Date of the connection, in the format YYYY-MM-DD.
                  Example: 2012-03-25
            time: Time of the connection, in the format hh:mm
                  Example: 17:30
            isArrivalTime: defaults to 0, if set to 1 the passed date and time
                           is the arrival time
                           Example: 1
            transportations: Transportation means; one or more of ice_tgv_rj,
                             ec_ic, ir, re_d, ship, s_sn_r, bus, cableway,
                             arz_ext, tramway_underground:
                             Example:
                                transportations[]=ec_ic&transportations[]=bus
            limit: 1 - 6. Specifies the number of connections to return. If
                   several connections depart at the same time they are counted
                   as 1.
                   Example: 2
            page: 0 - 10. Allows pagination of connections. Zero-based, so
                  first page is 0, second is 1, third is 2 and so on.
                  Example: 3
            direct: defaults to 0, if set to 1 only direct connections are
                    allowed.
                    Example: 1
            sleeper: defaults to 0, if set to 1 only night trains containing
                     beds are allowed, implies direct=1.
                     Example: 1
            couchette: defaults to 0, if set to 1 only night trains containing
                       couchettes are allowed, implies direct=1.
                       Example: 1
            bike: defaults to 0, if set to 1 only trains allowing the transport
                  of bicycles are allowed.
                  Example: 1
        """

        url = "http://transport.opendata.ch/v1/connections"

        kwargs['from'] = origin
        kwargs['to'] = destination

        self._format_datetime(kwargs, 'date', '%Y-%m-%d')
        self._format_datetime(kwargs, 'time', '%H:%M')

        self._bool_to_int(kwargs, 'isArrivalTime')

        response = self.http_get(url, kwargs)

        return response

    def get_stationboard(self, station=None, station_id=None, **kwargs):
        """station: Specifies the location of which a stationboard should
                    be returned: Aarau
        id: The id of the station whose stationboard should be returned.
            Alternative to the station parameter; one of these two is required.
            If both an id and a station are specified the id has precedence.:
            8503059 (for Zurich Stadelhofen)
        limit: Number of departing connections to return.
               This is not a hard limit - if multiple connections leave at
               the same time it'll return any connections that leave at the
               same time as the last connection within the limit.
               For example: limit=4 will return connections leaving at:
                    19:30
                    19:32
                    19:32
                    19:35
                    19:35
               Because one of the connections leaving at 19:35 is within
               the limit, all connections leaving at 19:35 are shown.: 15
        transportations: Transportation means; one or more of ice_tgv_rj,
                         ec_ic, ir, re_d, ship, s_sn_r, bus, cableway, arz_ext,
                         tramway_underground:
                            ?transportations[]=ec_ic&transportations[]=bus
        datetime: Date and time of departing connections, in the format
                  YYYY-MM-DD hh:mm.: 2012-03-25 17:30
        """

        url = "http://transport.opendata.ch/v1/stationboard"

        if station is None and station_id is None:
            raise ValueError("station or id needs a value.")

        if not station is None:
            kwargs['station'] = station

        if not station_id is None:
            kwargs['id'] = station_id

        self._format_datetime(kwargs, 'datetime', '%Y-%m-%d %H:%M')

        response = self.http_get(url, kwargs)

        return response

    def _format_datetime(self, params, key, format_):
        if key in params:
            params[key] = params[key].strftime(format_)

    def _bool_to_int(self, params, key):
        if key in params:
            params[key] = int(params[key])

    def http_get(self, base_url, params):
        url = "%s?%s" % (base_url, urllib.urlencode(params))
        logging.getLogger(__name__).info(url)
        req = urllib2.Request(url=url)
        response = urllib2.urlopen(req, timeout=2).read()
        # logging.getLogger(__name__).info(response)
        return json.loads(response)
