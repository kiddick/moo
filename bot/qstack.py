import os
import requests

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'pagenum.moo'), 'r') as pagenum:
    PAGE = int(pagenum.readlines()[0].rstrip())


API = 'https://api.stackexchange.com/2.2/questions'
QURL = 'https://stackoverflow.com/q'

data = {
    'page': PAGE,
    'pagesize': '1',
    'sort': 'votes',
    'tagged': 'python',
    'site': 'stackoverflow',
}


def nextq():
    r = requests.get(API, params=data)
    items = r.json()['items'][0]
    return ('{}/{}'.format(QURL, items['question_id']),
            items['title'])


def incrementq():
    with open(os.path.join(__location__, 'pagenum.moo'), 'w') as pagenum:
        pagenum.write(str(data['page'] + 1))
    data['page'] += 1
