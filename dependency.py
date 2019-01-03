# coding: utf8
import os
from typing import Dict

import util


def check_linguist(ctx: util.DotDict) -> Dict[str, bool]:
    """ Install linguist and check if it's installed successfully. """
    if util.run_with_check('which gem'):
        if not util.run('gem list --local -q github-linguist', check=False):
            util.run_with_check('gem install github-linguist', stdout=None)
    ruby_script = os.path.join(ctx.run_dir, 'linguist.rb')
    linguist_cmd = 'ruby {0} {1}'.format(ruby_script, ctx.run_dir)
    result = {
        'linguist_enabled': util.run_with_check(linguist_cmd),
    }
    return result
