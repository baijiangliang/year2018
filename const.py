# coding: utf8

GIT_EMAIL_CMD = 'git config --get user.email'
CHECK_GIT_DIR_CMD = 'git rev-parse --is-inside-work-tree'
GIT_COMMIT_SEPARATOR = 'git-commit-separator'
GIT_LOG_FORMAT = GIT_COMMIT_SEPARATOR + '%H%n%P%n%an%n%ae%n%at%n%s%n'
GIT_REMOTE_URL_CMD = 'git config --get remote.origin.url'
COMMIT_WEIGHT = 16
MAX_YEAR_DAY = 366
