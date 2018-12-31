# coding: utf8
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Set

import const
import util
import conf

git_clone_tmpl = 'git clone {git_url}'
git_log_tmpl = 'git log master --since="{begin}" --until="{end}"  --format="{fmt}" --numstat'
git_show_tmpl = 'git show {commit_id} --format="{fmt}"'

commit_weight = 16


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
            if repo.user_commits:
                self.repos.append(repo)

    def get_commit_summary(self):
        pass

    def get_most_common_repo(self):
        pass

    def get_commit_distribution(self, duration_type='hour') -> Dict[int, int]:
        commits = {}
        for repo in self.repos:
            for commit in repo.user_commits:
                if duration_type == 'hour':
                    duration = util.timestamp_to_datetime(commit.timestamp).hour
                elif duration_type == 'day_of_year':
                    duration = util.timestamp_to_day_of_year(commit.timestamp)
                else:
                    continue
                commits[duration] = commits.get(duration, 0) + 1
        return commits

    def get_latest_commit(self) -> Commit:
        """ Get the commit which has latest commit time. """
        latest_commit = latest_time = None
        for repo in self.repos:
            for commit in repo.user_commits:
                commit_time = util.timestamp_to_fixed_day(commit.timestamp)
                if latest_commit is None:
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

    def get_busiest_day(self) -> Tuple[datetime.date, Dict[str, int]]:
        """ Get the day which has max commit weight. """
        commits = {}
        for repo in self.repos:
            for commit in repo.user_commits:
                commit_day = util.timestamp_to_datetime(commit.timestamp).date()
                if commit_day not in commits:
                    commits[commit_day] = {
                        'commits': 1,
                        'insert': commit.code_ins,
                        'delete': commit.code_del,
                    }
                else:
                    commits[commit_day]['commits'] += 1
                    commits[commit_day]['insert'] += commit.code_ins
                    commits[commit_day]['delete'] += commit.code_del
        weights = []
        for day, stat in commits.items():
            weight = weight_commits(stat['commits'], stat['insert'], stat['delete'])
            weights.append((day, weight))
        weights.sort(key=lambda x: x[1], reverse=True)
        busiest_day = weights[0][0]
        return busiest_day, commits[busiest_day]

    def get_language_stat(self) -> Dict[str, Any]:
        res = {}
        for repo in self.repos:
            for commit in repo.user_commits:
                for lang, stat in commit.lang_stat.items():
                    if lang not in res:
                        res[lang] = {
                            'commits': 1,
                            'insert': stat['insert'],
                            'delete': stat['delete'],
                        }
                    else:
                        res[lang]['commits'] += 1
                        res[lang]['insert'] += stat['insert']
                        res[lang]['delete'] += stat['delete']
        for lang, stat in res.items():
            weight = weight_commits(stat['commits'], stat['insert'], stat['delete'])
            res[lang]['weight'] = weight
        return res

    def get_merge_relations(self) -> Dict[str, Dict[str, int]]:
        merges = {}
        # One author email may related to several author names, use the most readable name
        authors = {}
        for repo in self.repos:
            for commit in repo.commit_list:
                if len(commit.parents) == 1:
                    continue
                merged_id = commit.parents[1]
                merged = repo.get_commit_by_id(merged_id)
                if not merged:
                    continue
                # user merges his own commit
                if commit.email in self.ctx.emails and merged.email in self.ctx.emails:
                    continue
                # user merges others' commit
                elif commit.email in self.ctx.emails:
                    if merged.email not in merges:
                        merges[merged.email] = {}
                        authors[merged.email] = {merged.author}
                    else:
                        merges[merged.email]['merge'] = merges[merged.email].get('merge', 0) + 1
                        authors[merged.email].add(merged.author)
                # user's commit merged by others
                elif merged.email in self.ctx.emails:
                    if commit.email not in merges:
                        merges[commit.email] = {}
                        authors[commit.email] = {commit.author}
                    else:
                        merges[commit.email]['merged_by'] = merges[commit.email].get('merged_by',
                                                                                     0) + 1
                        authors[commit.email].add(commit.author)
        result = {}
        for email, stat in merges.items():
            name = choose_most_readable_name(authors[email])
            if name not in result:
                result[name] = stat
            else:
                result[name]['merge'] += stat['merge']
                result[name]['merged_by'] += stat['merged_by']
        return result


class Repo:
    def __init__(self, git_url_or_path: str, ctx: util.DotDict):
        if os.path.isdir(git_url_or_path):  # git repository path
            repo_dir = git_url_or_path
            os.chdir(repo_dir)
            if util.run(const.CHECK_GIT_DIR_CMD, check=False) != 'true':
                print('Error: {0} is not a git repository!'.format(self.git_dir))
                raise ValueError('Invalid git path!')
            repo_name = os.path.basename(repo_dir)
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
                    util.run(git_clone_tmpl.format(git_url=git_url_or_path), stdout=None)
                    print('Clone {0} succeed!'.format(git_url_or_path))
                except Exception as e:
                    print('Error: fail to clone {0}, reason: {1}'.format(git_url_or_path, e))
                    raise e
        self.git_dir = repo_dir
        self.name = repo_name
        self.git_url = util.run(const.GIT_REMOTE_URL_CMD, check=False)
        self.ctx = ctx
        self.commit_list = []
        self.commit_dict = {}
        self.user_commits = []
        self.parse_git_commits()

    def parse_git_commits(self):
        """ Parse commits in the given time range. """
        os.chdir(self.git_dir)
        git_log_cmd = git_log_tmpl.format(begin=self.ctx.begin, end=self.ctx.end,
                                          fmt=const.GIT_LOG_FORMAT)
        git_log = util.run(git_log_cmd)
        commit_logs = git_log.split(const.GIT_COMMIT_SEPARATOR)
        for commit_log in commit_logs:
            if not commit_log:
                continue
            commit = self.parse_git_log(commit_log)
            self.commit_list.append(commit)
            self.commit_dict[commit.id] = commit
            if commit.email in self.ctx.emails:
                self.user_commits.append(commit)

    def parse_git_log(self, commit_log: str) -> Commit:
        """ Parse formatted git log"""
        lines = commit_log.split('\n')
        if len(lines) < 7:
            raise ValueError("Wrong git log format: " + commit_log)
        commit = Commit(repo_name=self.name, commit_id=lines[0], parent_ids=lines[1].split(' '),
                        author=lines[2], email=lines[3], timestamp=int(lines[4]))
        commit.subject = lines[5]
        commit.num_stat = [line.strip() for line in lines[6:] if line.strip()]
        if commit.email in self.ctx.emails:
            Repo.parse_commit_stat(commit)
        return commit

    def get_commit_summary(self) -> Dict[str, Any]:
        res = {
            'commits': 0,
            'merges': 0,
            'insert': 0,
            'delete': 0,
        }
        for commit in self.user_commits:
            res['commits'] += 1
            if len(commit.parents) > 1:
                res['merges'] += 1
            res['insert'] += commit.code_ins
            res['delete'] -= commit.code_del
        return res

    def get_commit_by_id(self, commit_id) -> Any:
        commit = self.commit_dict.get(commit_id)
        # A very old commit, find it by git command
        if not commit:
            git_cmd = git_show_tmpl.format(commit_id=commit_id, fmt=const.GIT_LOG_FORMAT)
            try:
                res = util.run(git_cmd, check=True)
            except Exception as e:
                print(e)
                return
            commit_log = res.split(const.GIT_COMMIT_SEPARATOR)[0]
            commit = self.parse_git_log(commit_log)
        return commit

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
        if code_files > conf.max_files or code_ins > conf.max_insertions or code_del > \
                conf.max_deletions:
            code_files = code_files if code_files < conf.common_files else conf.avg_files
            code_ins = code_ins if code_ins < conf.common_insertions else conf.avg_insertions
            code_del = code_del if code_del < conf.common_deletions else conf.avg_deletions
            lang_stat = {}
        # Few changes, use total files stat
        elif total_files < conf.common_files and (total_ins + total_del) < conf.common_insertions:
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
        if first_dir in conf.ignore_dirs['common'] or '.' not in file_path:
            return language
        extension = file_path.rsplit('.', maxsplit=1)[-1].strip().lower()
        if extension in conf.code_file_extensions:
            language = conf.code_file_extensions[extension]
        if language in conf.ignore_dirs and first_dir in conf.ignore_dirs[language]:
            language = ''
        return language


def weight_commits(commit_times, insertions, deletions: int) -> int:
    return commit_times * commit_weight + insertions + deletions


def choose_most_readable_name(names: Set[str]) -> str:
    candidates = []
    for name in names:
        if not util.is_ascii(name):
            candidates.append(name)
    candidates = candidates if candidates else names
    return max(candidates, key=lambda x: len(x))
