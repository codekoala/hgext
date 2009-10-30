from hashlib import sha1
from mercurial import commands, util
from random import random
import hg
import os

def neclone(ui, source, dest='.', **opts):
    """Clones a Mercurial repository into a non-empty directory"""
    
    # make sure we don't have a repository in the destination directory already
    final_dest = os.path.join(dest, '.hg')
    if not os.access(final_dest, os.R_OK):
        util.Abort('There is already a Mercurial repository in %s!' % dest)
    
    # generate a random directory name to house the cloned repo temporarily
    hash = sha1(str(random())).hexdigest()
    tmp_dest = os.path.join(dest, hash)
    os.mkdir(tmp_dest)

    # clone the repo
    commands.clone(ui, source, tmp_dest, update=False, **opts)

    # move the cloned repo to the appropriate location
    os.rename(os.path.join(tmp_dest, '.hg'), final_dest)

    # clean up
    os.rmdir(tmp_dest)

commands.norepo += " neclone"
cmdtable = {
    'ngclone': (neclone, [] , "hg neclone SOURCE [DEST]")
}
