from mercurial import commands

def multi_push(ui, repo, **opts):
    """Pushes changesets out to all repos listed in the [paths] section of the config"""

    for name, location in ui.configitems('paths'):
        commands.push(ui, repo, location, **opts)

def multi_pull(ui, repo, **opts):
    """Pulls changesets in from all repos listed in the [paths] section of the config"""

    for name, location in ui.configitems('paths'):
        commands.pull(ui, repo, location, **opts)

cmdtable = {
    '^mpush': (multi_push, commands.table['^push'][1], commands.table['^push'][2].replace('[DEST]', '')),
    '^mpull': (multi_pull, commands.table['^pull'][1], commands.table['^pull'][2].replace('[SOURCE]', ''))
}
