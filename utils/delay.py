'''This module contains time calculation stuff for deferred tasks.'''

import logging

from pytz import timezone
from datetime import datetime

from config import Config

logging.getLogger(__name__).addHandler(logging.NullHandler())

TZ = timezone(Config.TIMEZONE)


def ready(hour, offset):
    '''Return nearest time to start in hours.'''
    if offset > 12:
        raise ValueError('Max value of offset is 12!')
    if hour < offset:
        return offset
    return hour if not hour / offset else (hour / offset + 1) * offset


def start_time(hour):
    '''Return nearest round time to start.'''
    now = datetime.now(TZ)
    if hour == 24:
        return now.replace(
            day=now.day + 1, hour=0, minute=0, second=0, microsecond=0)
    elif hour < now.hour:
        return now.replace(
            day=now.day + 1, hour=hour, minute=0, second=0, microsecond=0)
    else:
        return now.replace(
            hour=hour, minute=0, second=0, microsecond=0)


def total(offset, hour=datetime.now(TZ).hour):
    '''Return delay until start in seconds.'''
    delay = (start_time(ready(hour, offset)) -
             datetime.now(TZ)).total_seconds()
    logging.debug('Time until first run: %s', delay)
    return delay
