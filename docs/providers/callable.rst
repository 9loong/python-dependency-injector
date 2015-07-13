Callable providers
------------------

``Callable`` provider is a provider that wraps particular callable with
some injections. Every call of this provider returns result of call of initial
callable.

``Callable`` provider uses ``KwArg`` injections. ``KwArg`` injections are
done by passing injectable values as keyword arguments during call time.

Context keyword arguments have higher priority than ``KwArg`` injections.

Example:

.. image:: /images/callable.png
    :width: 100%
    :align: center

.. code-block:: python

    """`Callable` providers examples."""

    from objects.providers import Callable
    from objects.injections import KwArg


    class SomeCrypt(object):

        """Example class SomeCrypt."""

        @staticmethod
        def encrypt(data, password):
            """Encypt data using password."""
            return ''.join((password, data, password))

        @staticmethod
        def decrypt(data, password):
            """Decrypt data using password."""
            return data[len(password):-len(password)]


    # Encrypt and decrypt function providers:
    encrypt = Callable(SomeCrypt.encrypt,
                       KwArg('password', 'secret123'))
    decrypt = Callable(SomeCrypt.decrypt,
                       KwArg('password', 'secret123'))

    # Making some asserts:
    initial_data = 'some_data'

    encrypted1 = encrypt(initial_data)
    decrypted1 = decrypt(encrypted1)

    assert decrypted1 == initial_data

    # Context keyword arguments priority example:
    encrypted2 = encrypt(initial_data, password='another_secret')
    decrypted2 = decrypt(encrypted2)

    assert decrypted2 != initial_data
