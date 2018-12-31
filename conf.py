# coding: utf8

# Change directories you want to ignore here
ignore_dirs = {
    'common': [
        'vendor',
        'build',
    ],
    'Go': [
        'thrift_gen',
        'clients',  # This dir is not universal for Go, delete it if you don't want to ignore
    ],
    'Python': [
        'develop-eggs',
        'dist',
        'eggs',
        'lib',
        'lib64',
        'wheels',
        'env',
    ],
    'C++': [

    ],
    'Java': [

    ],
    'C': [

    ],
    'JavaScript': [

    ],
    'C#': [

    ],
    'Ruby': [

    ],
}

# If the commit stat exceeds limits in one commit, this commit will be considered as auto-generated
# change and be replaced with average commit stat.
max_files = 32
max_insertions = 2048
max_deletions = 2048

avg_files = 2
avg_insertions = 32
avg_deletions = 32

common_files = 8
common_insertions = 256
common_deletions = 256


code_file_extensions = {
    'py': 'Python',
    'go': 'Go',
    'c': 'C',
    'h': 'C++',
    'cpp': 'C++',
    'cc': 'C++',
    'hpp': 'C++',
    'java': 'Java',
    'js': 'JavaScript',
    'vue': 'JavaScript',
    'ts': 'TypeScript',
    'css': 'CSS',
    'less': 'CSS',
    'html': 'HTML',
    'cs': 'C#',
    'php': 'PHP',
    'r': 'R',
    'rb': 'Ruby',
    'm': 'Objective-C',
    'swift': 'Swift',
    'scala': 'Scala',
    'sh': 'Shell',
}