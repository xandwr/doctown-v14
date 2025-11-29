from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget

from flight_deck.widgets.top_bar import TopBar


class WindowLayout(Container):
    """A window container with topbar and content area - like BaseLayout.astro."""

    DEFAULT_CSS = """
    WindowLayout {
        width: 100%;
        height: 100%;
        border: solid $primary;
    }

    WindowLayout > .window-body {
        width: 100%;
        height: 1fr;
    }
    """

    def __init__(self, title: str = "Flight Deck", *children: Widget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.title_text = title
        self._child_widgets = children

    def compose(self) -> ComposeResult:
        yield TopBar(self.title_text)
        with Container(classes="window-body"):
            for child in self._child_widgets:
                yield child
