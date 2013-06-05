from unittest import TestCase

from mock import Mock

import giphypop


class GiphyTestCase(TestCase):

    def setUp(self):
        self.api = giphypy.Giphy()

    def test_search(self):
        self.api.search('popcorn')

    def test_translate(self):
        pass

    def test_screensaver(self):
        pass

    def test_gif(self):
        pass
