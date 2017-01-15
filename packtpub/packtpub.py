"""This module contains the stuff to check new free books on packtpub."""

import os
import logging
import collections

import requests
import lxml.html
import werkzeug

from config import Config

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

logging.getLogger(__name__).addHandler(logging.NullHandler())


PPUB_URL = 'https://www.packtpub.com/'
OFFER_URL = '{}packt/offers/free-learning'.format(PPUB_URL)
BOOK_URL = '{}ebook_download/{}/pdf'.format(PPUB_URL, '{}')

HEADERS = {
    'Host': ' www.packtpub.com',
    'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': ' en-US,en;q=0.5',
    'Accept-Encoding': ' gzip, deflate, br',
    'Referer': ' https://www.packtpub.com/',
    'Connection': ' keep-alive',
    'User-Agent':  'Mozilla/5.0 Gecko/20100101 Firefox/45.0'
}

PAYLOAD = {
    'email': Config.PPUB_EMAIL,
    'password': Config.PPUB_PASSWORD,
    'form_id': 'packt_user_login_form',
    'op': 'Login',
}


Book = collections.namedtuple('Book', 'label img claim_url')


def get_book_filename(url):
    filename_part = url.split('?')[0]
    return filename_part.split('/')[-1]


def visit():
    headers = {'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/45.0'}
    try:
        r = requests.get(OFFER_URL, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.exception(e)
        return
    doc = lxml.html.fromstring(r.content)
    try:
        label = doc.xpath('.//div[@class="dotd-title"]/h2')[0].text.strip()
        img = doc.xpath(
            (
                '. // div[@class="dotd-main-book-image float-left"]'
                '/a/img/@data-original'
            )
        )[0]
        claim_url = doc.xpath('.//a[@class="twelve-days-claim"]/@href')[0]
    except Exception as e:
        logging.exception(e)
        return
    img = 'https://' + werkzeug.urls.url_fix(img).lstrip('/')
    return Book(label, img, claim_url)


def check():
    feed = os.path.join(__location__, 'feed.moo')
    if not os.path.isfile(feed):
        open(feed, 'w').close()
    with open(feed, 'r') as _:
        labels = _.readlines()
        if labels:
            last_label = labels[-1].rstrip()
    book = visit()
    if not book:
        return None, 'Something wrong! Check logs.'
    if not last_label or last_label != book.label:
        with open(feed, 'a') as _:
            _.write('{}\n'.format(book.label.encode('utf-8')))
        return book, None
    return None, 'No updates!'


def fetch_book(url, filename):
    path = os.path.join(Config.PPUB_BOOKS, filename)
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as _:
            for chunk in r:
                _.write(chunk)
    return path


def download_book(claim_url):
    s = requests.Session()

    # login request
    s.post(PPUB_URL, data=PAYLOAD, headers=HEADERS)

    full_claim_url = '{}{}'.format(PPUB_URL, claim_url.lstrip('/'))
    book_id = claim_url.strip('/').split('/')[1]

    # add book to account
    s.get(full_claim_url, headers=HEADERS)

    # get direct link to storage with book
    r = s.get(BOOK_URL.format(book_id), headers=HEADERS, allow_redirects=False)
    book_url = r.headers['location']

    # downloading from storage
    return fetch_book(book_url, get_book_filename(book_url))


_, _, claim_url = visit()
download_book(claim_url)
