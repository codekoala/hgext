from mercurial import hg, commands, util
import os

LOG_KEY = '^log|history'
SERVE_KEY = '^serve'

def_prop = lambda k, i: commands.table[k][i]

def _get_patch_queue_repo(ui, repo):
    """Attempts to get the repository for any existing patch queue"""
    pq_dir = os.path.join(repo.root, '.hg', 'patches')
    if not os.path.exists(pq_dir):
        raise util.Abort('This repository has no patch queues.  Please install the `mq` extension and use `qinit` to create one.')

    return hg.repository(ui, pq_dir)

def qlog(ui, repo, **opts):
    """Runs the hg log command for the patch queue repo of a regular repo"""
    pq_repo = _get_patch_queue_repo(ui, repo)
    commands.log(ui, pq_repo, **opts)

def qserve(ui, repo, **opts):
    """Runs hg serve for the patch queue repository of a regular repo"""
    pq_repo = _get_patch_queue_repo(ui, repo)
    commands.serve(ui, pq_repo, **opts)

cmdtable = {
    'qlog': (qlog, def_prop(LOG_KEY, 1), def_prop(LOG_KEY, 2)),
    'qserve': (qserve, def_prop(SERVE_KEY, 1), def_prop(SERVE_KEY, 2)),
}
