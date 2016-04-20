"""This module contains the stuff to check new free books on packtpub."""

import os
import logging

import requests
import lxml.html
import werkzeug

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

logging.getLogger(__name__).addHandler(logging.NullHandler())

OFFER_URL = 'https://www.packtpub.com/packt/offers/free-learning'


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
            './/div[@class="dotd-main-book-image float-left"]/a/img/@data-original')[0]
    except Exception as e:
        logging.exception(e)
        return
    img = 'https://' + werkzeug.urls.url_fix(img).lstrip('/')
    return label, img


def check():
    feed = os.path.join(__location__, 'feed.moo')
    if not os.path.isfile(feed):
        open(feed, 'w').close()
    with open(feed, 'r') as _:
        book = _.readlines()
        if book:
            book = book[-1].rstrip()
    result = visit()
    if result:
        label, img = result
    else:
        return 'Something wrong! Check logs.'
    if not book or book != label:
        with open(feed, 'a') as _:
            _.write('{}\n'.format(label))
        return label, img
    return 'No updates!'
