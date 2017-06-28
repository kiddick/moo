import pytest

from bot import packtpub


def test_real_request():
    book = packtpub.visit()
    print(book)
