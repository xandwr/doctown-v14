"""
CommonsScreen - browse public/shared docpacks.

Future home for:
- Browsing community-shared docpacks
- Searching public knowledge bases
- One-click import of popular docpacks

For now, a placeholder with coming soon messaging.
"""

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Label, Static

from flight_deck.widgets import NavBar


class CommonsScreen(Screen):
    """Browse public docpacks - coming soon."""

    DEFAULT_CSS = """
    CommonsScreen {
        layout: vertical;
    }

    CommonsScreen .page-content {
        width: 100%;
        height: 1fr;
        align: center middle;
    }

    CommonsScreen .coming-soon-box {
        width: 60;
        height: auto;
        padding: 3 4;
        border: round $primary;
        background: $surface;
    }

    CommonsScreen .coming-soon-icon {
        width: 100%;
        text-align: center;
        color: $primary;
        padding-bottom: 1;
    }

    CommonsScreen .coming-soon-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    CommonsScreen .coming-soon-text {
        width: 100%;
        text-align: center;
        color: $text-muted;
    }

    CommonsScreen .feature-list {
        width: 100%;
        padding-top: 2;
        color: $text-muted;
    }

    CommonsScreen .feature-item {
        padding-left: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield NavBar(active="commons")

        with Center(classes="page-content"):
            with Vertical(classes="coming-soon-box"):
                yield Label("📚", classes="coming-soon-icon")
                yield Label("The Commons", classes="coming-soon-title")
                yield Label(
                    "A public library of shared docpacks",
                    classes="coming-soon-text",
                )
                yield Label("Coming soon...", classes="coming-soon-text")

                with Vertical(classes="feature-list"):
                    yield Label("Planned features:", classes="coming-soon-text")
                    yield Label("• Browse community docpacks", classes="feature-item")
                    yield Label("• Search public knowledge bases", classes="feature-item")
                    yield Label("• One-click import & explore", classes="feature-item")
                    yield Label("• Share your own docpacks", classes="feature-item")
