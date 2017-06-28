import pytest

from bot import packtpub


def test_real_visit():
    book = packtpub.visit()
    print(book)
    assert book


def test_real_download():
    book = packtpub.visit()
    print book.claim_url
    print(packtpub.download_book(book.claim_url))
