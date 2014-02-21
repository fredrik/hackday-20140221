import urwid


palette = [
    ('header', 'white', 'black'),
    ('reveal focus', 'black', 'dark cyan', 'standout')
]


items = [urwid.Text("foo"),
         urwid.Text("bar"),
         urwid.Text("baz")]

content = urwid.SimpleListWalker(
    [urwid.AttrMap(w, None, 'reveal focus') for w in items]
)


body = urwid.ListBox(content)
header = urwid.Text(u"oh hai")

frame = urwid.Frame(body, header)


def handle_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


def main():
    loop = urwid.MainLoop(frame, palette, unhandled_input=handle_input)
    loop.run()


if __name__ == '__main__':
    main()
