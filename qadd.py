from mercurial import hg, commands, util
from hgext import mq
import os
import re

LOG_KEY = '^log|history'
SERVE_KEY = '^serve'
PUSH_KEY = '^push'

MAGIC_RE = re.compile('\((?P<type>\w+):(?P<pattern>.+?)\) (?P<url>.*)', re.M | re.S)

def_prop = lambda k, i: commands.table[k][i]

def qrepo(ui, repo):
    """Attempts to get the repository for any existing patch queue"""
    q = repo.mq
    if not q:
        raise util.Abort('This repository has no patch queues.  Please install the `mq` extension and use `qinit` to create one.')

    return q

def qlog(ui, repo, **opts):
    """Runs the hg log command for the patch queue repo of a regular repo"""
    q = qrepo(ui, repo)
    commands.log(ui, q, **opts)

def pushq(ui, repo, dest=None, **opts):
    """Runs the hg push command for the patch queue repo of a regular repo"""

    q = qrepo(ui, repo)
    commands.push(ui, hg.repository(q.path), dest, **opts)

def qserve(ui, repo, **opts):
    """Runs hg serve for the patch queue repository of a regular repo"""
    q = qrepo(ui, repo)
    commands.serve(ui, q, **opts)

def qreorder(ui, repo, new_index, patch_name=None, **opts):
    """Moves a patch in your patch queue to a different place in the series.

    If you do not specify the patch name, the currently applied patch will be 
    moved to the new location.  The index must be 1 or greater."""

    q = qrepo(ui, repo)
    p = repo.mq

    # get the current patch name
    if p.applied:
        current_patch = p.applied[-1].name

        # remove all applied patches
        q.pop(repo, all=True)
    else:
        current_patch = None

    if not patch_name:
        if not current_patch:
            raise util.Abort('Please specify a patch to move.')
        else:
            patch_name = current_patch
    else:
        patch_name = q.lookup(patch_name)

    patch_name += '\n'

    # make sure the new position is valid
    try:
        new_index = int(new_index)
        if new_index < 1:
            raise ValueError
    except ValueError, err:
        raise util.Abort('Invalid new position argument.  Please use a positive integer.')

    # manipulate the queue series ordering
    status_path = os.path.join(q.path, 'status')
    series_path = os.path.join(q.path, 'series')

    ui.write('Moving patch "%s" to position %i in patch series...\n' % (patch_name.strip(), new_index))
    series = [l for l in open(series_path, 'r')]
    series.remove(patch_name)
    if new_index > len(series) + 1:
        series.append(patch_name)
    else:
        series.insert(new_index - 1, patch_name)

    # update the series and status files
    open(series_path, 'w').writelines(series)
    open(status_path, 'w').write('')

    if current_patch:
        # reapply all patches up to the previously applied patch
        new_repo = hg.repository(ui, os.path.join(repo.root)) # refresh the series
        mq.goto(ui, new_repo, current_patch, force=False)

def qticket(ui, repo, patch_name, **opts):
    """Attempts to open a web browser to the location for the ticket that a patch addresses"""

    q = qrepo(ui, repo)
    patch = q.lookup(patch_name)

    import webbrowser

    ticket_urls = ui.configitems('ticket_urls')
    for name, magic in ticket_urls:
        match = MAGIC_RE.search(magic)
        if match:
            match_type, pattern, url = match.groups()

            if match_type == 'file':
                match_using = patch
            elif match_type == 'contents':
                patch_file = os.path.join(q.path, patch)
                match_using = open(patch_file, 'r').readline()
            else:
                util.Abort('Invalid match type in policy %s: %s.  Options are "file" and "contents"\n' % (name, match_type))

            magic_match = re.match(pattern, match_using)

            if magic_match:
                # replace junk in the URL with info from the patch
                the_url = re.sub(pattern, url, match_using).strip()
                if the_url != patch:
                    webbrowser.open(the_url)
        else:
            util.Abort('Invalid ticket magic in policy %s: %s\n' % (name, magic))

cmdtable = {
    'qlog': (qlog, def_prop(LOG_KEY, 1), def_prop(LOG_KEY, 2)),
    'pushq': (pushq, def_prop(PUSH_KEY, 1), def_prop(PUSH_KEY, 2)),
    'qserve': (qserve, def_prop(SERVE_KEY, 1), def_prop(SERVE_KEY, 2)),
    'qreorder': (qreorder, [], 'hg qreorder NEW_POSITION [PATCH]'),
    'qticket': (qticket, [], 'hg qticket [PATCH]'),
}
