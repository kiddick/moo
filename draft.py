import os

import git

from config import Config


REPO = Config.REPO
GTOKEN = Config.GTOKEN


def bookmark(category, record):
    with open(os.path.join(REPO, category, '{}.md'.format(category)), 'a') as book:
        book.write('<hr>\n{}\n'.format(record.markdown()))


def push():
    repo = git.Repo(REPO)
    repo.git.add('--all')
    repo.git.commit(m='Add new record.')
    repo.git.push(
        'https://kiddick:{}@github.com/kiddick/draft.git'.format(GTOKEN))
