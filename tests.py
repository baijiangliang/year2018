# coding: utf8
import os
import unittest

import util
from report import Reporter


class TestReporter(unittest.TestCase):
    def setUp(self):
        run_dir = os.path.dirname(os.path.realpath(__file__))
        self.ctx = util.DotDict({
            'run_dir': run_dir,
            'name': 'baijiangliang',
            'emails': ['baijiangliang@gmail.com'],
            'git_inputs': [run_dir],
            'encrypt': True,
            'year': 2018,
            'begin': 1514736000,
            'end': 1546272000,
            'linguist_enabled': False
        })

    def test_reporter(self):
        reporter = Reporter(self.ctx)
        reporter.generate_report()


if __name__ == '__main__':
    unittest.main()
