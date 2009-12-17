from mercurial import commands
import re

def_prop = lambda k, i: commands.table[k][i]

LOOK_FOR = 'TODO:'
TODO_RE = re.compile('^(?P<file>.*?):(?P<rev>\d+):(?P<line>\d+):.*?(?P<match>%s.*)$' % LOOK_FOR, re.M)

GREP = 'grep'

def todo_finder(ui, repo, *pats, **opts):
    """Searches for TODO items in your repository"""

    persist = opts.pop('write', None)
    opts['line_number'] = True

    class WriteCaptor(object):
        def __init__(self):
            self.matches = []

        def capture(self, text, eol):
            self.matches.append(text + eol)

    format = lambda matches: ['File:\t%s\nLine:\t%s\n%s\n\n' % (m[0], m[2], m[3]) for m in todos]

    captor = WriteCaptor()

    orig_write = ui.write
    ui.write = captor.capture
    commands.grep(ui, repo, LOOK_FOR, *pats, **opts)
    ui.write = orig_write

    todos = TODO_RE.findall('\n'.join(captor.matches))
    if persist:
        open(persist, 'w').writelines(format(todos))
    else:
        ui.write('%s' % ''.join(format(todos)))

cmdtable = {
    '^todo|tg': (todo_finder, def_prop(GREP, 1) + [
                    ('w', 'write', '', 'write all TODOs to the specified file'),
                ], '[OPTION]'),
}

