import warnings

from collections import namedtuple

import requests


GIPHY_API_ENDPOINT = 'http://api.giphy.com/v1/gifs'

# Note this is a public beta key and may be inactive at some point
GIPHY_PUBLIC_KEY = 'dc6zaTOxFJmzC'


class GiphyApiException(Exception):
    pass


class GiphyResult(dict):

    def __getattr__(self, attr):
        print 'Getting', attr
        if hasattr(self, attr):
            return getattr(self, attr)
        else:
            return self.get(attr, u'')

    def __setattr__(self, attr, value):
        print 'Setting', attr
        if hasattr(self, attr):
            super(GiphyResult, self).__setattr__(attr)
        else:
            self[attr] = value


class Giphy(object):
    """
    A python wrapper around the Giphy Api
    """

    def __init__(self, api_key=GIPHY_PUBLIC_KEY):
        # Warn if using public key
        if api_key == GIPHY_PUBLIC_KEY:
            warnings.warn('The giphy public key is for beta testing the api and may be deprecated',
                          PendingDeprecationWarning)

        self.api_key = api_key

    def _endpoint(self, name):
        return '/'.join((GIPHY_API_ENDPOINT, name))

    def _check_or_raise(self, meta):
        if meta.get('status') != 200:
            raise GiphyApiException(meta.get('error_message'))

    def _make_result(self, data):
        result = GiphyResult(id=data.get('id'),
                             url=data.get('url'),
                             type=data.get('type'))

        # bitly urls
        result.bitly = GiphyResult(fullscreen=data.get('bitly_fullscreen_url'),
                                   tiled=data.get('bitly_tiled_url'),
                                   gif=data.get('bitly_gif_url'))

        images = data.get('images', {})
        result.images = GiphyResult((k, GiphyResult(**v)) for k, v in images.iteritems())

        return result

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
        }

        resp = requests.get(self._endpoint('search'), params=params)
        resp.raise_for_status()

        data = resp.json()
        self._check_or_raise(data.get('meta'))

        return [self._make_result(result) for result in data['data']]
