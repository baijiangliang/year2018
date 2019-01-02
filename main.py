# coding: utf8
"""Generate annual report for programmers."""
import traceback
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
                dir_path = os.path.join(root, dir_name)
                if util.is_git_dir(dir_path):
                    git_inputs.append(dir_path)
    print('请选择是否对报告中的项目名、人名等进行加密，默认不加密(开启加密后，year2018 会变成 ye****18)')
    encrypt = False
    option = input('是否加密(y/n)，输入 y 开启\n').strip()
    if option.lower() == 'y':
        encrypt = True
    info = {
        'name': name,
        'emails': list(set(emails)),
        'git_inputs': list(set(git_inputs)),
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
        if key == 'git_inputs':
            print('git_inputs: ')
            print(' '.join(val))
            continue
        print(key + ': ' + str(val))
    print('报告生成中...')
    try:
        reporter = Reporter(ctx)
        reporter.generate_report()
        print('报告生成成功')
        print('请到 ' + reporter.output_dir + ' 查看你的年度编程报告')
    except Exception as e:
        print(e)
        traceback.print_exc()
        print('报告生成失败')
        print('请到 ' + const.REPO_URL + ' 提 issue')


if __name__ == '__main__':
    main()
