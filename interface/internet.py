import urwid

palette = [
    ('header', 'white', 'black'),
    ('reveal focus', 'black', 'dark cyan', 'standout')
]

# items = [urwid.Text("foo"),
#          urwid.Text("bar"),
#          urwid.Text("baz")]

# content = urwid.SimpleListWalker([urwid.AttrMap(w, None, 'reveal focus') for w in items])

listbox = urwid.ListBox([])

# show_key = urwid.Text("Press any key", wrap='clip')
# head = urwid.AttrMap(show_key, 'header')
# top = urwid.Frame(listbox, head)

top = urwid.Frame(listbox)


loop = urwid.MainLoop(top, palette)
loop.run()

