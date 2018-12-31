# coding: utf8
"""Generate annual report for programmers."""
import os
import time
from datetime import datetime
from typing import Dict, Any

import const
import util
from report import Reporter

RUN_DIR = os.path.dirname(os.path.realpath(__file__))


def get_user_info() -> Dict[str, Any]:
    """ Get information from user's inputs. """
    print('Sometimes it is the people no one imagines anything of, who do the things no one can '
          'imagine.\n' + ' ' * 70 + '-- Alan Turing')
    print('欢迎使用程序员年度总结生成器')
    while True:
        name = input('请输入你的名字，按回车继续\n').strip()
        if name:
            break
    print('请输入你近一年使用过的 git 邮箱，不输入则使用 ${0} 的结果'.format(const.GIT_EMAIL_CMD))
    emails = []
    while True:
        email_input = input('git 邮箱(一行一个或者空格分隔)：\n').strip()
        if not email_input:
            break
        emails.extend(email_input.split())
    if not emails:
        email = util.run(const.GIT_EMAIL_CMD)
        if not email:
            raise Exception('No valid git email!')
        emails.append(email)
    print('请输入你近一年参与开发的所有仓库的 git 地址($git remote -v)或本地路径，不输入则在上一级目录下自动搜索')
    git_inputs = []
    while True:
        git_input = input('git 地址或本地路径(一行一个或者空格分隔)：\n').strip()
        if not git_input:
            break
        git_inputs.extend(git_input.split())
    # Try to find git repositories in parent directory
    if not git_inputs:
        parent_dir = os.path.join(RUN_DIR, os.pardir)
        for root, dirs, files in os.walk(parent_dir):
            for dir_name in dirs:
                if dir_name.startswith('.') or dir_name == 'year2018':
                    continue
                git_dir = os.path.join(root, dir_name)
                os.chdir(git_dir)
                if util.run(const.CHECK_GIT_DIR_CMD, check=False) == 'true':
                    git_inputs.append(git_dir)
            break
    print('请选择是否对输出结果进行加密，默认不加密(开启加密后，year2018 会变成 ye****18)')
    encrypt = False
    option = input('是否加密(y/n)，输入 y 开启\n').strip()

    if option.lower() == 'y':
        encrypt = True

    info = {
        'name': name,
        'emails': emails,
        'git_inputs': git_inputs,
        'encrypt': encrypt,
    }
    return info


def get_time_info() -> Dict[str, int]:
    """ Get recent year's info. """
    now = datetime.now()
    recent_year = now.year
    if now.month == 1:
        recent_year -= 1
    begin_ts = time.mktime(datetime(year=recent_year, month=1, day=1).timetuple())
    end_ts = time.mktime(datetime(year=recent_year + 1, month=1, day=1).timetuple())
    year_ends = {
        'year': recent_year,
        'begin': int(begin_ts),
        'end': int(end_ts),
    }
    return year_ends


def main():
    ctx = util.DotDict()
    ctx.run_dir = RUN_DIR
    ctx.update(get_user_info())
    ctx.update(get_time_info())
    print('\nContext:')
    for key, val in ctx.items():
        print(key + ': ' + str(val))
    reporter = Reporter(ctx)
    reporter.get_commit_graph()


if __name__ == '__main__':
    main()
