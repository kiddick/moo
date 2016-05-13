import os

import yaml

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'settings.yaml')) as ysttgs:
    settings = yaml.load(ysttgs)


class Config(object):
    DEBUG = settings['debug']
    LREPO = settings['draft_repo']
    GREPO = settings['github_repo']
    GTOKEN = settings['github_token']
    BTOKEN = settings['bot_token']
