try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

from mercurial import commands, util
from random import random
import os

def neclone(ui, source, dest='.', **opts):
    """Clones a Mercurial repository into a non-empty directory"""
    
    # make sure we don't have a repository in the destination directory already
    base = os.path.abspath(dest)
    final_dest = os.path.join(base, '.hg')
    if os.path.exists(final_dest):
        raise util.Abort('There is already a Mercurial repository in `%s`!  Clone aborted.' % base)
    
    # generate a random directory name to house the cloned repo temporarily
    hash = sha1(str(random())).hexdigest()
    tmp_dest = os.path.join(base, hash)

    # ensure that our temporary directory exists
    try:
        os.makedirs(tmp_dest)
    except OSError, err:
        pass

    # clone the repo
    opts['noupdate'] = True
    commands.clone(ui, source, tmp_dest, **opts)

    # move the cloned repo to the appropriate location
    os.rename(os.path.join(tmp_dest, '.hg'), final_dest)

    # clean up
    os.rmdir(tmp_dest)

commands.norepo += " neclone"
cmdtable = {
    'neclone': (neclone, 
    commands.table['^clone'][1], 
    commands.table['^clone'][2])
}
