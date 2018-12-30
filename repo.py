# coding: utf8
import os
from datetime import datetime
from typing import List, Dict, Any

import const
import util
from  config import ignore_dirs, code_file_extensions

git_clone_tmpl = 'git clone {git_url}'
git_log_tmpl = 'git log master --since="{begin}" --until="{end}"  --format="{format}" --numstat'
git_show_tmpl = 'git show {hash} --format="{format}"'


class Commit:
    def __init__(self, repo_name, commit_id: str, parent_ids: List[str], author, email: str,
                 timestamp: int):
        self.repo_name = repo_name
        self.id = commit_id
        self.parents = parent_ids
        self.author = author
        self.email = email
        self.timestamp = timestamp
        self.subject = ''
        self.num_stat = []
        self.code_ins = 0
        self.code_del = 0
        self.code_files = 0
        self.lang_stat = {}


class Repos:
    def __init__(self, ctx: util.DotDict):
        self.ctx = ctx
        self.repos = []
        for git_input in ctx.git_inputs:
            repo = Repo(git_input, ctx)
            self.repos.append(repo)

    def get_commit_distribution(self, duration_type='hour'):
        commits = {}
        for repo in self.repos:
            for commit in repo.commit_list:
                if duration_type == 'hour':
                    duration = util.timestamp_to_hour(commit.timestamp)
                elif duration_type == 'day_of_year':
                    duration = util.timestamp_to_day_of_year(commit.timestamp)
                else:
                    continue
                commits[duration] = commits.get(duration, 0) + 1
        return commits

    def get_latest_commit(self) -> Commit:
        latest_commit, latest_time = None, None
        for repo in self.repos:
            for commit in repo.commit_list:
                if commit.email not in self.ctx.emails:
                    continue
                commit_time = datetime.fromtimestamp(commit.timestamp).replace(year=2018, month=1,
                                                                               day=1)
                if not latest_commit:
                    latest_commit, latest_time = commit, commit_time
                    continue
                # commit before dawn
                if latest_time.hour < 6:
                    if commit_time.hour < 6 and commit_time > latest_time:
                        latest_commit, latest_time = commit, commit_time
                else:
                    if commit_time.hour < 6 or commit_time > latest_time:
                        latest_commit, latest_time = commit, commit_time
        return latest_commit


class Repo:
    def __init__(self, git_url_or_path: str, ctx: util.DotDict):
        if os.path.isdir(git_url_or_path):  # git repository path
            os.chdir(git_url_or_path)
            if util.run(const.CHECK_GIT_DIR_CMD, check=False) != 'true':
                print('Error: {0} is not a git repository!'.format(self.git_dir))
                raise ValueError('Invalid git path!')
            self.git_dir = git_url_or_path
            repo_name = os.path.basename(git_url_or_path)
        else:  # git remote url
            repo_parent_dir = os.path.join(ctx.run_dir, 'user_repos')
            if not os.path.exists(repo_parent_dir):
                os.mkdir('user_repos')
            os.chdir(repo_parent_dir)
            repo_name = git_url_or_path.rsplit('/', 1)[-1].split('.')[0]
            repo_dir = os.path.join(repo_parent_dir, repo_name)
            # clone repository if not exists
            if not os.path.exists(repo_dir):
                try:
                    util.run(git_clone_tmpl.format(git_url_or_path), stdout=None)
                except Exception as e:
                    print('Error: fail to clone {0}, reason: {1}'.format(git_url_or_path, e))
                    raise e
            self.git_dir = repo_dir
        self.name = repo_name
        self.git_url = util.run(const.GIT_REMOTE_URL_CMD, check=False)
        self.ctx = ctx
        self.commit_list = []
        self.commit_dict = {}
        self.parse_git_commits()

    def parse_git_commits(self):
        """ Parse commits in the given time range. """
        os.chdir(self.git_dir)
        git_log_cmd = git_log_tmpl.format(begin=self.ctx.begin, end=self.ctx.end,
                                          format=const.GIT_LOG_FORMAT)
        print(git_log_cmd)
        git_log = util.run(git_log_cmd)
        commit_logs = git_log.split('git-commit-separator\n')
        for commit_log in commit_logs:
            if not commit_log:
                continue
            commit = self.parse_git_log(commit_log)
            self.commit_list.append(commit)
            self.commit_dict[commit.id] = commit

    def parse_git_log(self, commit_log: str) -> Commit:
        """ Parse formatted git log"""
        lines = commit_log.split('\n')
        if len(lines) < 7:
            raise ValueError("Wrong git log format: " + commit_log)
        commit = Commit(repo_name=self.name, commit_id=lines[0], parent_ids=lines[1].split(' '),
                        author=lines[2], email=lines[3], timestamp=int(lines[4]))
        commit.subject = lines[5]
        commit.num_stat = [line.strip() for line in lines[6:] if line.strip()]
        Repo.parse_commit_stat(commit)
        return commit

    def get_commit_summary(self) -> Dict[str, Any]:
        res = {
            'commits': 0,
            'merges': 0,
            'insert': 0,
            'delete': 0,
        }
        for commit in self.commit_list:
            if commit['email'] not in self.ctx.emails:
                continue
            res['commits'] += 1
            if len(commit['parent_hashes']) > 1:
                res['merges'] += 1
            res['insert'] += commit.code_ins
            res['delete'] -= commit.code_del
        return res

    @staticmethod
    def parse_commit_stat(commit: Commit):
        total_files, code_files = len(commit.num_stat), 0
        total_ins = total_del = code_ins = code_del = 0
        lang_stat = {}
        for line in commit.num_stat:
            insert, delete, file_name = line.split(maxsplit=2)
            if insert == '-':  # binary file
                continue
            insert, delete = int(insert), int(delete)
            total_ins += insert
            total_del += delete
            lang = Repo.detect_code_file(file_name)
            if not lang:
                continue
            code_files += 1
            code_ins += insert
            code_del += delete
            if lang not in lang_stat:
                lang_stat[lang] = {
                    'insert': insert,
                    'delete': delete,
                }
            else:
                lang_stat[lang]['insert'] += insert
                lang_stat[lang]['delete'] += delete
        # Too much changes, considered as auto generated code: library code, thrift source code,
        # auto-format code, etc. Use averaged guess instead.
        if code_files > 32 or code_ins > 2048 or code_del > 2048:
            code_files = code_files if code_files < 8 else 4
            code_ins = code_ins if code_ins < 256 else 32
            code_del = code_del if code_del < 256 else 32
            lang_stat = {}
        # Few changes, use total files stat
        elif total_files < 8 and (total_ins + total_del) < 256:
            code_files, code_ins, code_del = total_files, total_ins, total_del
        commit.code_files = code_files
        commit.code_ins = code_ins
        commit.code_del = code_del
        commit.lang_stat = lang_stat

    @staticmethod
    def detect_code_file(file_path: str) -> str:
        """
        Detect which programming language is used in the file .
        """
        # TODO use more sophisticated method
        language = ''
        first_dir = file_path.split('/', maxsplit=1)[0].strip()
        if first_dir in ignore_dirs['common'] or '.' not in file_path:
            return language
        extension = file_path.rsplit('.', maxsplit=1)[-1].strip().lower()
        if extension in code_file_extensions:
            language = code_file_extensions[extension]
        if language in ignore_dirs and first_dir in ignore_dirs[language]:
            language = ''
        return language
