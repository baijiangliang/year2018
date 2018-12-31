# coding: utf8
import subprocess
from  datetime import datetime
from typing import List, Any


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


def rescale_to_interval(nums: List[Any], lower_bound=0, upper_bound=1) -> List[float]:
    """ Rescale numbers to interval [lower_bound, upper_bound]. """
    high, low = max(nums), min(nums)
    if high - low == 0:
        return [upper_bound for _ in nums]
    result = []
    for num in nums:
        scaled = (num - low) / (high - low) * upper_bound
        if scaled < lower_bound:
            scaled = lower_bound
        result.append(scaled)
    return result
