from mercurial import commands

def_prop = lambda k, i: commands.table[k][i]

PUSH = '^push'
OUTGOING = 'outgoing|out'
PULL = '^pull'
INCOMING = 'incoming|in'

def do_multi(func, ui, repo, **opts):
    """Iterates over each path in the [paths] section of the config"""

    for name, location in ui.configitems('paths'):
        try:
            func(ui, repo, location, **opts)
        except (ValueError, AttributeError) as err:
            ui.warn('Failed to perform operation on repo: %s\n\t>>> %s\n' % (location, err))

def multi_push(ui, repo, **opts):
    """Pushes changesets out to all repos listed in the [paths] section of the config"""

    do_multi(commands.push, ui, repo, **opts)

def multi_outgoing(ui, repo, **opts):
    """Determines which changesets would be pushed to each repo listed in the [paths] section of the config"""

    do_multi(commands.outgoing, ui, repo, **opts)

def multi_pull(ui, repo, **opts):
    """Pulls changesets in from all repos listed in the [paths] section of the config"""

    do_multi(commands.pull, ui, repo, **opts)

def multi_incoming(ui, repo, **opts):
    """Determines which changesets would be pulled in from each repos listed in the [paths] section of the config"""

    do_multi(commands.incoming, ui, repo, **opts)

cmdtable = {
    '^mpush': (multi_push, def_prop(PUSH, 1), def_prop(PUSH, 2).replace('[DEST]', '')),
    '^moutgoing': (multi_outgoing, def_prop(OUTGOING, 1), def_prop(OUTGOING, 2).replace('[DEST]', '')),
    '^mpull': (multi_pull, def_prop(PULL, 1), def_prop(PULL, 2).replace('[SOURCE]', '')),
    '^mincoming': (multi_incoming, def_prop(INCOMING, 1), def_prop(INCOMING, 2).replace('[SOURCE]', '')),
}
