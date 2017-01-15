import os

import yaml

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'settings.yaml')) as ysttgs:
    settings = yaml.load(ysttgs)


class Config(object):
    DEBUG = settings['debug']
    LOGGING_LEVEL = settings['logging_level']

    LREPO = settings['draft_repo']
    GREPO = settings['github_repo']
    GTOKEN = settings['github_token']
    BTOKEN = settings['bot_token']

    PPUB_EMAIL = settings['ppub_email']
    PPUB_PASSWORD = settings['ppub_password']
    PPUB_BOOKS = settings['ppub_books_path']

    TIMEZONE = settings['timezone']
    JOB_INTERVAL = settings['job_interval']
