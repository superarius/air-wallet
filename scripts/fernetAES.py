#!/usr/bin/python3
# USAGE:
# message = 'John Doe'
# >>> password = 'mypass'
# >>> password_encrypt(message.encode(), password)
# b'9Ljs-w8IRM3XT1NDBbSBuQABhqCAAAAAAFyJdhiCPXms2vQHO7o81xZJn5r8_PAtro8Qpw48kdKrq4vt-551BCUbcErb_GyYRz8SVsu8hxTXvvKOn9QdewRGDfwx'
# >>> token = _
# >>> password_decrypt(token, password).decode()
# 'John Doe'


import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getpass import getpass
import sys

backend = default_backend()
iterations = 100_000


def _derive_key(password: bytes, salt: bytes,
                iterations: int = iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))


def password_encrypt(message: bytes, password: str,
                     iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def password_decrypt(token: bytes, password: str) -> bytes:
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)


# start here:
if __name__ == '__main__':
    if 3>len(sys.argv):
        raise ValueError(f'provide command line args encrypt|decrypt path/to/encrypted/file')
    args = sys.argv[1:]
    command = args[0]
    filepath = args[1]
    if command == 'encrypt':
        msg = getpass('message: ')
        pw = getpass('password: ')
        encrypted = password_encrypt(msg.encode(), pw)
        with open(filepath, 'wb') as f:
            f.write(encrypted)
        print(f'encryption stored: {filepath}')
    elif command == 'decrypt':
        pw = getpass('password: ')
        msg = 'error decrypting'
        with open(filepath, 'rb') as f:
            encrypted = f.read()
            msg = password_decrypt(encrypted, pw).decode()
        print(msg)
    else:
        raise ValueError(f'unrecognized command line argument: {command} for [ encrypt , decrypt ]')
            
