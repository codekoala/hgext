from mercurial import commands
import re

def_prop = lambda k, i: commands.table[k][i]

LOOK_FOR = 'TODO:'
TODO_RE = re.compile('^(?P<file>.*?):(?P<rev>\d+):(?P<line>\d+):.*?(?P<match>%s.*)$' % LOOK_FOR, re.M)

GREP = 'grep'

def format(todo_dict):
    file_count = len(todo_dict)
    todo_count = sum(len(todos) for todos in todo_dict.values())

    output = 'Found %i TODOs in %i files\n\n' % (todo_count, file_count)

    for file, todos in todo_dict.items():
        output += "File:\t%s\n" % file

        for line, todo in todos:
            output += "\tLine: %s\t%s\n" % (line, todo)

        output += "\n"

    return output

def todo_finder(ui, repo, *pats, **opts):
    """Searches for TODO items in your repository"""

    persist = opts.pop('write', None)
    opts['line_number'] = True

    class WriteCaptor(object):
        def __init__(self):
            self.matches = []

        def capture(self, text, eol):
            self.matches.append(text + eol)

    captor = WriteCaptor()

    orig_write = ui.write
    ui.write = captor.capture
    commands.grep(ui, repo, LOOK_FOR, *pats, **opts)
    ui.write = orig_write

    todos = TODO_RE.findall('\n'.join(captor.matches))

    # group the TODOs by file
    todo_dict = {}
    for file, rev, line, todo in todos:
        if not todo_dict.has_key(file):
            todo_dict[file] = []

        todo_dict[file].append((line, todo))

    formatted = format(todo_dict)

    if persist:
        open(persist, 'w').write(formatted)
    else:
        ui.write(formatted)

cmdtable = {
    '^todo|tg': (todo_finder, def_prop(GREP, 1) + [
                    ('w', 'write', '', 'write all TODOs to the specified file'),
                ], '[OPTION]'),
}

