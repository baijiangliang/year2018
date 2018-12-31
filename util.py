# coding: utf8
import subprocess
from  datetime import datetime


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


def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


def timestamp_to_day_of_year(timestamp: int) -> int:
    dt = datetime.fromtimestamp(timestamp)
    return dt.timetuple().tm_yday


def timestamp_to_fixed_day(timestamp: int) -> datetime:
    dt = datetime.fromtimestamp(timestamp)
    return dt.replace(year=2018, month=1, day=1)


def is_ascii(s: str) -> bool:
    return all(ord(c) < 128 for c in s)
