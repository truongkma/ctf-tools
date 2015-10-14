.. _api:

Developer Interface
===================

.. module:: paddingoracle

This part of the documentation covers all the interfaces exposed by the
Padding Oracle Exploit API.


Main Interface
--------------

Tool authors should subclass the :class:`PaddingOracle` class and implement
:meth:`oracle`. A typical example may look like::

    from paddingoracle import PaddingOracle, BadPaddingException

    class PadBuster(PaddingOracle):
        def oracle(self, data):

            #
            # code to determine if a padding oracle is revealed
            # if a padding oracle is revealed, raise a BadPaddingException
            #

            raise BadPaddingException

To exploit the padding oracle vulnerability, simply::

    padbuster = PadBuster()
    decrypted = padbuster.decrypt(encrypted_data)

    print decrypted

That's all!  The hard work of actually carrying out the attack is handled
in the :meth:`PaddingOracle.bust` method (not documented), which in turns
calls the :meth:`~PaddingOracle.oracle` method implemented by your code.

.. autoclass:: PaddingOracle
    :members: decrypt, encrypt, oracle, analyze


Exceptions
----------

.. autoexception:: BadPaddingException
