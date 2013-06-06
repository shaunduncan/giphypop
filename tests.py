from unittest import TestCase

from mock import Mock, patch

from giphypop import AttrDict, Giphy, GiphyApiException, GiphyImage


# TEST DATA
FAKE_DATA = {
    "bitly_fullscreen_url": "http://gph.is/XH7Sri",
    "bitly_gif_url": "http://gph.is/XH7V6j",
    "bitly_tiled_url": "http://gph.is/XH7Srk",
    "id": "3avUsGhmckIYE",
    "images": {
        "fixed_height": {
            "height": "200",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/200.gif",
            "width": "289"
        },
        "fixed_height_downsampled": {
            "height": "200",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/200_d.gif",
            "width": "289"
        },
        "fixed_height_still": {
            "height": "200",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/200_s.gif",
            "width": "289"
        },
        "fixed_width": {
            "height": "138",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/200w.gif",
            "width": "200"
        },
        "fixed_width_downsampled": {
            "height": "138",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/200w_d.gif",
            "width": "200"
        },
        "fixed_width_still": {
            "height": "138",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/200w_s.gif",
            "width": "200"
        },
        "original": {
            "height": "346",
            "url": "http://media.giphy.com/media/3avUsGhmckIYE/giphy.gif",
            "width": "500",
            "frames": "100",
            "size": "123",
        }
    },
    "type": "gif",
    "url": "http://giphy.com/gifs/3avUsGhmckIYE"
}


class AttrDictTestCase(TestCase):

    def test_get_attribute_raises(self):
        foo = AttrDict()
        self.assertRaises(AttributeError, lambda: foo.bar)

    def test_get_attribte(self):
        foo = AttrDict(bar='baz')
        assert foo.bar == 'baz'

    def test_get_attribute_proxies_key(self):
        foo = AttrDict(bar='baz')
        foo['bar'] = 'baz'
        assert foo.bar == 'baz'

    def test_set_attribute(self):
        foo = AttrDict()
        foo.bar = 'baz'
        assert foo.bar == 'baz'

    def test_set_attribute_proxies_key(self):
        foo = AttrDict()
        foo.bar = 'baz'
        assert foo['bar'] == 'baz'

    def test_hasattr(self):
        foo = AttrDict(bar='baz')
        assert hasattr(foo, 'bar')
        assert not hasattr(foo, 'baz')

    def test_with_property(self):
        class Foo(AttrDict):
            @property
            def foo(self):
                return 'bar'

        foo = Foo()
        assert foo.foo == 'bar'


class GiphyImageCase(TestCase):

    def test_normalize(self):
        result = GiphyImage()
        norm = result._normalized({
            'width': '200',
            'height': 300,
            'something': 'foo',
            'frames': '100',
            'size': '1234567890'
        })

        assert isinstance(norm['width'], int)
        assert isinstance(norm['height'], int)
        assert isinstance(norm['frames'], int)
        assert isinstance(norm['size'], int)
        assert isinstance(norm['something'], str)

    def test_make_images_creates_attribute(self):
        # Expect that make_images will create an attribute with key name
        result = GiphyImage()
        img = {'original': FAKE_DATA['images']['original']}

        assert not hasattr(result, 'original')
        result._make_images(img)
        assert hasattr(result, 'original')

    def test_make_images_doesnt_subattr(self):
        # If there is a single underscore, don't subattr
        result = GiphyImage()
        img = {'fixed_width': FAKE_DATA['images']['fixed_width']}

        assert not hasattr(result, 'fixed')
        assert not hasattr(result, 'fixed_width')
        result._make_images(img)
        assert not hasattr(result, 'fixed')
        assert hasattr(result, 'fixed_width')

    def test_make_images_creates_subattr(self):
        result = GiphyImage()
        img = {'fixed_width': FAKE_DATA['images']['fixed_width'],
               'fixed_width_still': FAKE_DATA['images']['fixed_width_still']}

        assert not hasattr(result, 'fixed_width')
        result._make_images(img)
        assert hasattr(result, 'fixed_width')
        assert hasattr(result.fixed_width, 'still')

    def test_original_properties(self):
        result = GiphyImage()
        img = {'original': FAKE_DATA['images']['original']}
        props = {
            'media_url': 'url',
            'frames': 'frames',
            'width': 'width',
            'height': 'height',
            'filesize': 'size'
        }

        for prop in props:
            self.assertRaises(AttributeError, lambda: getattr(result, prop))

        result._make_images(img)

        for prop, attr in props.items():
            assert getattr(result, prop) == getattr(result.original, attr)


class GiphyTestCase(TestCase):

    def setUp(self):
        self.g = Giphy()

    def test_endpoint(self):
        assert self.g._endpoint('search') == 'http://api.giphy.com/v1/gifs/search'

    def test_check_or_raise_raises(self):
        self.assertRaises(GiphyApiException, self.g._check_or_raise, {'status': 400})

    def test_check_or_raise_no_status(self):
        self.assertRaises(GiphyApiException, self.g._check_or_raise, {})

    def test_check_or_raise(self):
        assert self.g._check_or_raise({'status': 200}) is None

    @patch('giphypop.requests')
    def test_fetch_error_raises(self, requests):
        # api returns error messages sorta like...
        err = {'meta': {'error_type': 'ERROR', 'code': 400, 'error_message': ''}}
        requests.get.return_value = requests
        requests.json.return_value = err

        self.assertRaises(GiphyApiException, self.g._fetch, 'foo')

    def fake_search_fetch(self, num_results, pages=3):
        self.g._fetch = Mock()
        self.g._fetch.return_value = {
            'data': [FAKE_DATA for x in range(num_results)],
            'pagination': {
                'total_count': pages,
                'count': 25,
                'offset': 0
            },
            'meta': {'status': 200}
        }

    def fake_fetch(self, result=FAKE_DATA):
        self.g._fetch = Mock()
        self.g._fetch.return_value = {
            'data': result or None,
            'meta': {'status': 200}
        }

    def test_search_no_results(self):
        self.fake_search_fetch(0, pages=1)
        results = [x for x in self.g.search('foo')]
        assert len(results) == 0

    def test_search_respects_hard_limit(self):
        self.fake_search_fetch(25)
        results = [x for x in self.g.search('foo', limit=10)]
        assert len(results) == 10

    def test_search_handles_pages(self):
        self.fake_search_fetch(25)
        results = [x for x in self.g.search('foo', limit=50)]
        assert len(results) == 50

    def test_search_no_limit_returns_all(self):
        self.fake_search_fetch(25)
        results = [x for x in self.g.search('foo', limit=None)]
        assert len(results) == 75

    def test_search_list_returns_list(self):
        self.fake_search_fetch(25)
        results = self.g.search_list('foo', limit=10)
        assert isinstance(results, list)
        assert len(results) == 10

    def test_search_with_phrase_hyphenates(self):
        self.fake_search_fetch(0, pages=1)
        self.g.search(phrase='foo bar baz')
        assert self.g._fetch.called_with(q='foo-bar-baz')

    def test_translate_with_phrase_hyphenates(self):
        self.fake_fetch()
        self.g.translate(phrase='foo bar baz')
        assert self.g._fetch.called_with(s='foo-bar-baz')

    def test_translate(self):
        self.fake_fetch()
        assert isinstance(self.g.translate('foo'), GiphyImage)
        assert self.g._fetch.called_with('translate')

    def test_gif(self):
        self.fake_fetch()
        assert isinstance(self.g.gif('foo'), GiphyImage)
        assert self.g._fetch.called_with('foo')

    def test_screensaver(self):
        self.fake_fetch()
        assert isinstance(self.g.screensaver(), GiphyImage)

    def test_screensaver_passes_tag(self):
        self.fake_fetch()
        self.g.screensaver('foo')
        assert self.g._fetch.called_with(tag='foo')

    def test_random_gif(self):
        self.fake_fetch()
        assert isinstance(self.g.random_gif(), GiphyImage)

    def test_translate_returns_none(self):
        self.fake_fetch(result=None)
        assert self.g.translate('foo') is None

    def test_gif_returns_none(self):
        self.fake_fetch(result=None)
        assert self.g.gif('foo') is None

    def test_screensaver_returns_none(self):
        self.fake_fetch(result=None)
        assert self.g.screensaver('foo') is None

    def test_translate_raises_strict(self):
        self.fake_fetch(result=None)
        self.assertRaises(GiphyApiException, self.g.translate, 'foo', strict=True)

    def test_gif_returns_raises_strict(self):
        self.fake_fetch(result=None)
        self.assertRaises(GiphyApiException, self.g.gif, 'foo', strict=True)

    def test_screensaver_raises_strict(self):
        self.fake_fetch(result=None)
        self.assertRaises(GiphyApiException, self.g.screensaver, 'foo', strict=True)
