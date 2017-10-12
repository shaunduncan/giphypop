giphypop
========

``giphypop`` is a wrapper around the Giphy_ api. It aims to provide a more
intuitive, pythonic way for interacting with the Giphy_ api.

.. image:: https://secure.travis-ci.org/shaunduncan/giphypop.png?branch=master
   :target: https://travis-ci.org/shaunduncan/giphypop


Requirements, Installing, and Compatibility
-------------------------------------------

The only requirement, included in ``requirements.txt`` is for requests_. If you
are using pip, you can install ``giphypop``:

.. code-block:: bash

    $ pip install requests giphypop

Alternatively:

.. code-block:: bash

    $ pip install requests
    $ pip install -e git+https://github.com/shaunduncan/giphypop.git#egg=giphypop

Then you should be off and running. ``giphypop`` has been tested against python
versions 2.6, 2.7, 3.2 and 3.3.


Getting Started
---------------

Using ``giphypop`` is straightforward and aims provide interaction with
the api without any regard to large bits of JSON. To get started, you
can test out various features using the include api key. You should be
warned, however, that while Giphy_ has been so kind as have a public
"testing" key, it may be turned off in the future. See the `api docs`_
for more information.

The entry point for interacting with Giphy_ api is the ``giphypop.Giphy``
class. This class optionally accepts three arguments: ``api_key``, ``lang`` and ``strict``.
The ``api_key`` agument, when not preset, will default to the public key
(see above). The ``lang`` argument allows to pass custom language support to Giphy API request (see `Language Support`_).
The ``strict`` argument controls how you expect the api to
react when no results are returned. If enabled, an exception is raised,
otherwise, ``None`` is returned.


.. code-block:: python

    >>> import giphypop
    >>> g = giphypop.Giphy()

Now you're ready to get started. There are a few key methods of the
``giphypop.Giphy`` object that you'll want to know about

search
++++++
Search for gifs with a given word or phrase. Punctuation is ignored.
By default, this will perform a ``term`` search. If you want to search
by phrase, use the ``phrase`` keyword argument. What's the difference
between ``term`` and ``phrase`` searches? Simple: a term search will
return results matching any words given, whereas a phrase search will
match all words.

Note that this method is a ``giphypop.GiphyImage`` generator that
automatically handles api paging. Optionally accepts a limit that will
terminate the generation after a specified number of results have been
yielded. This defaults to 25 results; a None implies no limit

- **term**: Search term or terms, string
- **phrase**: Search phrase, string
- **limit**: Maximum number of results to yield, integer

search_list
+++++++++++
Suppose you expect the ``search`` method to just give you a list rather
than a generator. This method will have that effect. Equivalent to:

.. code-block:: python

    >>> g = giphypop.Giphy()
    >>> results = [x for x in g.search('foo')]

translate
+++++++++
Retrieve a single image that represents a transalation of a term or
phrase into an animated gif. Punctuation is ignored. By default, this
will perform a ``term`` translation. If you want to translate by phrase,
use the ``phrase`` keyword argument.

- **term**: Search term or terms, string
- **phrase**: Search phrase, string
- **strict**: Whether an exception should be raised when no results, boolean

gif
+++
Retrieves a specifc gif from giphy based on unique id

- **gif_id**: Unique giphy gif ID, string
- **strict**: Whether an exception should be raised when no results, boolean

screensaver
+++++++++++
Returns a random giphy image, optionally based on a search of a given tag.
Note that this method will both query for a screensaver image and fetch the
full details of that image (2 request calls)

- **tag**: Limit random gifs returned by a tag, string
- **strict**: Whether an exception should be raised when no results, boolean

random_gif
++++++++++
An alias of ``giphypop.Giphy.screensaver``

upload
++++++
Uploads a video or gif to giphy. Once the upload has completed, requests the
full gif details and returns a GiphyImage (2 request calls).

- **tags**: A list of tags to use on the uploaded gif, list
- **file_path**: The path to the file to upload, string
- **username**: The username of the account to upload to when using your own API key, string

------------------------------------------------------------------------------

.. note::
    The above methods of ``giphypop.Giphy`` are also exposed at the module
    level for your convenience. The only difference is that they also
    accept an ``api_key`` keyword argument. For example:

    .. code-block:: python

        >>> from giphypop import translate
        >>> img = translate('foo', api_key='bar')

------------------------------------------------------------------------------


Handling Results
----------------

All results that represent a single image are wrapped in a
``giphypop.GiphyImage`` object. This object acts like a dictionary, but
also exposes keys as attributes. Note, that these are **not** a direct
mirror of api response objects; their goal is to be simpler. Structure
follows this layout::

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

For example:

.. code-block:: python

    >>> from giphypop import translate
    >>> img = translate('foo')
    >>> img.url
    'http://giphy.com/foo/bar/baz'
    >>> img.width
    200
    >>> img.fixed_height.downsampled.url
    'http://giphy.com/foo/bar/downsampled'


Uploading
---------

The Giphy API will accept uploads of gifs or videos. You are able to upload
using the public API key, but you won't be able to assign them to your username
or delete them. In order to upload to your account, set the `username` when you
and the API key when you upload.

For example:

.. code-block:: python

    >>> from giphypop import upload
    >>> gif = upload(["foo", "bar"], "mycat.gif")
    >>> gif
    GiphyImage<26BRvG76mOYcvRxss> at http://giphy.com/gifs/bar-foo-26BRvG76mOYcvRxss

Or using your own API key to upload to your own account:

.. code-block:: python

    >>> from giphypop import upload
    >>> gif = upload(["foo", "bar"], "mycat.gif", username="gifsarefun", api_key="abcdef12345678")
    >>> gif
    GiphyImage<26BRvG76mOYcvRxss> at http://giphy.com/gifs/bar-foo-26BRvG76mOYcvRxss


Changelog
---------

0.1
+++

- Initial Version


Contribution and License
------------------------

Developed by `Shaun Duncan`_ and is licensed under the terms of a MIT license.
Contributions are welcomed and appreciated!


.. _Giphy: http://giphy.com
.. _requests: https://pypi.python.org/pypi/requests/1.2.3
.. _`api docs`: http://github.com/giphy/giphyapi
.. _`Shaun Duncan`: shaun.duncan@gmail.com
.. _`Language Support`: https://developers.giphy.com/docs/#language-support
