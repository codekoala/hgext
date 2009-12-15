from mercurial import commands

def multi_push(ui, repo, **opts):
    """Pushes changesets out to all repos listed in the [paths] section of the config"""

    for name, location in ui.configitems('paths'):
        commands.push(ui, repo, location, **opts)

cmdtable = {
    '^mpush': (multi_push, 
    commands.table['^push'][1], 
    commands.table['^push'][2].replace('[DEST]', ''))
}
