# coding: utf8
import subprocess
import time
from  datetime import datetime
from typing import Dict


class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def run(cmd: str, shell=True, stdout=subprocess.PIPE, timeout=600, check=True) -> str:
    """ Wrapper function of subprocess.run(). """
    res = subprocess.run(cmd, shell=shell, stdout=stdout, timeout=timeout, check=check)
    if res.stdout is None:
        return ''
    return res.stdout.decode('utf8').strip()


def get_recent_year_ends() -> Dict[str, int]:
    """ Get recent year's ends. """
    now = datetime.now()
    begin_year = now.year
    if now.month == 1:
        begin_year -= 1
    begin_ts = time.mktime(datetime(year=begin_year, month=1, day=1).timetuple())
    end_ts = time.mktime(datetime(year=begin_year + 1, month=1, day=1).timetuple())
    year_ends = {
        'year': begin_year,
        'begin': int(begin_ts),
        'end': int(end_ts),
    }
    return year_ends


def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


def timestamp_to_hour(timestamp: int) -> int:
    dt = datetime.fromtimestamp(timestamp)
    return dt.hour


def timestamp_to_day_of_year(timestamp: int) -> int:
    dt = datetime.fromtimestamp(timestamp)
    return dt.timetuple().tm_yday
