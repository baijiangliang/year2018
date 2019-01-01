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


def get_percents(nums: List[Any], ratio=100) -> List[float]:
    total = sum(nums)
    if total == 0:
        total = 1
    return [num / total * ratio for num in nums]


def get_name_from_email(email: str) -> str:
    return email.split('@')[0].split('.')[0]


def encrypt_name(name: str, encrypt=False) -> str:
    if not encrypt:
        return name
    size = len(name)
    if size <= 1:
        return name
    elif size <= 3:
        if is_ascii(name):
            return name
        else:
            return '*' + name[1:]
    elif size <= 5:
        return '*' * 2 + name[2:]
    else:
        return '*' * 3 + name[3:]


def encrypt_string(string: str, encrypt=False) -> str:
    if not encrypt:
        return string
    size = len(string)
    if size <= 2:
        return string
    elif size <= 5:
        return string[:2] + '*' * (size - 2)
    else:
        return string[:2] + '*' * (size - 4) + string[-2:]
