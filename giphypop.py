import warnings

import requests


GIPHY_API_ENDPOINT = 'http://api.giphy.com/v1/gifs'

# Note this is a public beta key and may be inactive at some point
GIPHY_PUBLIC_KEY = 'dc6zaTOxFJmzC'


class AttrDict(dict):
    """
    A subclass of dict that exposes keys as attributes
    """
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]

        try:
            return self[attr]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, attr))

    def __setattr__(self, attr, value):
        if attr in self.__dict__:
            self.__dict__[attr] = value
        else:
            self[attr] = value


class GiphyResult(AttrDict):
    """
    A special case AttrDict that handles data specifically being returned
    from the giphy api (i.e. integer values converted from strings). The structure
    is very object-like, but retains all the qualities of a python dict.
    Attributes are not a direct mirror of giphy api results, but follow this pattern::

        <Result Object>
            - id
            - type: image type (i.e. gif)
            - url: URL to giphy page
            - raw_data: copy of original data response from giphy (JSON)
            - fullscreen: bit.ly link to giphy fullscreen gif
            - tiled: bit.ly link to giphy tiled gif
            - bitly: bit.ly version of `url`
            - media_url: URL directly to image (original size)
            - frames: number of frames
            - height: image height (original image)
            - width: image width (original image)
            - size: filesize (in bytes, original image)
            - fixed_height: (variable width @ 200px height)
                - url: URL directly to image
                - width: image width
                - height: image height
                - downsampled:
                    - url: URL directly to image
                    - width: image width
                    - height: image height
                - still: (a still image of gif)
                    - url: URL directly to image
                    - width: image width
                    - height: image height
            - fixed_width: (variable height @ 200px width)
                - url: URL directly to image
                - width: image width
                - height: image height
                - downsampled:
                    - url: URL directly to image
                    - width: image width
                    - height: image height
                - still: (a still image of gif)
                    - url: URL directly to image
                    - width: image width
                    - height: image height
    """
    def __init__(self, data=None):
        if data:
            super(GiphyResult, self).__init__(id=data.get('id'),
                                              url=data.get('url'),
                                              type=data.get('type'),
                                              raw_data=data)

            # bit.ly urls
            self.fullscreen = data.get('bitly_fullscreen_url')
            self.tiled = data.get('bitly_tiled_url')
            self.bitly = data.get('bitly_gif_url')

            # Shorthand
            self._make_images(data.get('images', {}))

    @property
    def media_url(self):
        """
        The media URL of the gif at its original size
        """
        return self.original.url

    @property
    def frames(self):
        """
        The number of frames of the gif
        """
        return self.original.frames

    @property
    def width(self):
        """
        The width of the gif at its original size
        """
        return self.original.width

    @property
    def height(self):
        """
        The height of the gif at its original size
        """
        return self.original.height

    @property
    def filesize(self):
        """
        The size of the original size file in bytes
        """
        return self.original.size

    def _make_images(self, images):
        """
        Takes an image dict from the giphy api and converts it to attributes.
        Any fields expected to be int (width, height, size, frames) will be attempted
        to be converted. Also, the keys of `data` serve as the attribute names, but
        with special action taken. Keys are split by the last underscore; anything prior
        becomes the attribute name, anything after becomes a sub-attribute. For example:
        fixed_width_downsampled will end up at `self.fixed_width.downsampled`
        """
        # Order matters :)
        process = ('original',
                   'fixed_width',
                   'fixed_height',
                   'fixed_width_downsampled',
                   'fixed_width_still',
                   'fixed_height_downsampled',
                   'fixed_height_still')

        for key in process:
            data = images.get(key)

            # Ignore empties
            if not data:
                continue

            parts = key.split('_')

            # attr/subattr style
            if len(parts) > 2:
                attr, subattr = '_'.join(parts[:-1]), parts[-1]
            else:
                attr, subattr = '_'.join(parts), None

            # Normalize data
            img = AttrDict(self._normalized(data))

            if subattr is None:
                setattr(self, attr, img)
            else:
                setattr(getattr(self, attr), subattr, img)

    def _normalized(self, data):
        """
        Does a normalization of sorts on image type data so that values
        that should be integers are converted from strings
        """
        int_keys = ('frames', 'width', 'height', 'size')

        for key in int_keys:
            if key not in data:
                continue

            try:
                data[key] = int(data[key])
            except ValueError:
                pass  # Ignored

        return data


class GiphyApiException(Exception):
    pass


class Giphy(object):
    """
    A python wrapper around the Giphy Api
    """

    def __init__(self, api_key=GIPHY_PUBLIC_KEY):
        # Warn if using public key
        if api_key == GIPHY_PUBLIC_KEY:
            warnings.warn(u'You are using the giphy public api key. This should be used for testing only')

        self.api_key = api_key

    def _endpoint(self, name):
        return '/'.join((GIPHY_API_ENDPOINT, name))

    def _check_or_raise(self, meta):
        if meta.get('status') != 200:
            raise GiphyApiException(meta.get('error_message'))

    def search(self, term=None, phrase=None, limit=None, offset=0):
        """
        Search for gifs with a given word or phrase. Punctuation is ignored.
        By default, this will perform a `term` search. If you want to search
        by phrase, use the `phrase` keyword argument.

        :param term: Search term or terms
        :type term: string
        :param phrase: Search phrase
        :type phrase: string
        :param limit: Number of results to return (maximum 25)
        :type limit: int
        :param offset: Results offset (0-indexed)
        :type offset: int
        """
        assert any((term, phrase)), u'You must supply a term or phrase to search'

        if limit is not None:
            assert limit <= 25, u'Search limits must be <= 25'

        # Phrases should have dashes and not spaces
        if phrase:
            phrase = phrase.replace(' ', '-')

        params = {
            'q': term or phrase,
            'api_key': self.api_key,
            'offset': offset,
            'limit': limit,
        }

        resp = requests.get(self._endpoint('search'), params=params)
        resp.raise_for_status()

        data = resp.json()
        self._check_or_raise(data.get('meta'))

        # TODO: Make this a generator
        # TODO: Handle pagination after generator
        return [GiphyResult(img) for img in data['data']]

    def translate(self, term=None, phrase=None):
        """
        Retrieve a single image that represents a transalation of a term or
        phrase into an animated gif. Punctuation is ignored. By default, this
        will perform a `term` translation. If you want to translate by phrase,
        use the `phrase` keyword argument.

        :param term: Search term or terms
        :type term: string
        :param phrase: Search phrase
        :type phrase: string
        """
        assert any((term, phrase)), u'You must supply a term or phrase to search'

        # Phrases should have dashes and not spaces
        if phrase:
            phrase = phrase.replace(' ', '-')

        params = {
            's': term or phrase,
            'api_key': self.api_key,
        }

        resp = requests.get(self._endpoint('translate'), params=params)
        resp.raise_for_status()

        data = resp.json()
        self._check_or_raise(data.get('meta'))

        return GiphyResult(data['data'])

    def gif(self, gif_id):
        """
        Retrieves a specifc gif from giphy based on unique id

        :param gif_id: Unique giphy gif ID
        :type gif_id: string
        """
        params = {
            'api_key': self.api_key,
        }

        resp = requests.get(self._endpoint(gif_id), params=params)
        resp.raise_for_status()

        data = resp.json()
        self._check_or_raise(data.get('meta'))

        return GiphyResult(data['data'])

    def screensaver(self, tag=None):
        """
        Returns a random giphy image, optionally based on a search of a given tag.
        Note that this method will both query for a screensaver image and fetch the
        full details of that image (2 request calls)

        :param tag: Tag to retrieve a screensaver image
        :type tag: string
        """
        params = {
            'api_key': self.api_key,
        }

        if tag:
            params['tag'] = tag

        resp = requests.get(self._endpoint('screensaver'), params=params)
        resp.raise_for_status()

        data = resp.json()
        self._check_or_raise(data.get('meta'))

        return self.gif(data['data']['id'])
