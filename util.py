# coding: utf8
import os
import subprocess
import time
from  datetime import datetime
from typing import List, Any, Tuple

import const


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


def run_with_check(cmd: str, capture=True, timeout=600) -> bool:
    """ Return true if cmd ran successfully else false. """
    try:
        subprocess.run(cmd, shell=True, capture_output=capture, timeout=timeout, check=True)
    except Exception as e:
        print(e)
        return False
    return True


def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


def timestamp_to_day_of_year(timestamp: int) -> int:
    dt = datetime.fromtimestamp(timestamp)
    return dt.timetuple().tm_yday


def timestamp_to_fixed_day(timestamp: int) -> datetime:
    dt = datetime.fromtimestamp(timestamp)
    return dt.replace(year=2018, month=1, day=1)


def get_year_ends(year: int) -> Tuple[int, int]:
    begin_ts = time.mktime(datetime(year=year, month=1, day=1).timetuple())
    end_ts = time.mktime(datetime(year=year + 1, month=1, day=1).timetuple())
    return int(begin_ts), int(end_ts)


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


def get_percents(nums: List[Any], ratio=100, digits=2) -> List[float]:
    total = sum(nums)
    if total == 0:
        total = 1
    return [round(num / total * ratio, digits) for num in nums]


def get_name_from_email(email: str) -> str:
    return email.split('@')[0].rsplit('.', maxsplit=1)[0]


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
    elif size <= 6:
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
    elif size <= 9:
        return string[:2] + '*' * (size - 4) + string[-2:]
    else:
        return string[:3] + '*' * (size - 6) + string[-3:]


def is_git_dir(dir_path: str) -> bool:
    """ Check if the given directory is a git repository. """
    if not os.path.isdir(dir_path):
        return False
    os.chdir(dir_path)
    return run_with_check(const.CHECK_GIT_DIR_CMD)
