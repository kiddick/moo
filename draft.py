import os

import git
import requests
import lxml.html

from config import Config


LREPO = Config.LREPO
GREPO = Config.GREPO
GTOKEN = Config.GTOKEN



def header(link):
    try:
        r = requests.get(link)
        doc = lxml.html.fromstring(r.text)
        header = doc.find(".//title").text.encode('utf-8')
        return header
    except:
        return


def bookmark(category, record):
    title = header(record.link)
    if title:
        record.link = '[{0}]({1})'.format(title, record.link)
    with open(os.path.join(LREPO, category, '{}.md'.format(category)), 'a') as book:
        book.write('<hr>\n{}\n'.format(record.markdown()))


def push(m='Add new record.'):
    repo = git.Repo(LREPO)
    repo.git.add('--all')
    repo.git.commit(m)
    repo.git.push(
        'https://kiddick:{token}@{repo}'.format(token=GTOKEN, repo=GREPO.split('//')[1]))

def add_question(content):
    with open(os.path.join(LREPO, 'stackoverflow', 'questions.md'), 'a') as pyq:
            pyq.write(content)    
