"""
NavBar widget - persistent sticky header for Flight Deck.

Web-style navigation bar with:
- Left: Doctown ASCII logo
- Right: Navigation buttons (Commons, Generate, Explore)

Designed to feel like a website header while being terminal-native.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Static


# Tiny ASCII figlet logo for doctown
DOCTOWN_LOGO = """┌─┐┌─┐┌─┐┌┬┐┌─┐┬ ┬┌┐┌
│ ││ ││   │ │ │││││││
└─┘└─┘└─┘ ┴ └─┘└┴┘┘└┘"""

# Even more compact single-line version
DOCTOWN_LOGO_COMPACT = "◈ doctown"


class NavBar(Static):
    """Sticky navigation bar - website-style header."""

    class Navigate(Message):
        """Fired when a nav button is clicked."""

        def __init__(self, destination: str) -> None:
            super().__init__()
            self.destination = destination

    DEFAULT_CSS = """
    NavBar {
        dock: top;
        width: 100%;
        height: 3;
        background: $surface;
        border-bottom: solid $primary;
    }

    NavBar > Horizontal {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    NavBar .logo-section {
        width: auto;
        height: 100%;
        padding: 0 2;
        content-align: left middle;
    }

    NavBar .logo {
        color: $primary;
        text-style: bold;
    }

    NavBar .nav-spacer {
        width: 1fr;
    }

    NavBar .nav-section {
        width: auto;
        height: 100%;
        align: right middle;
        padding: 0 1;
    }

    NavBar .nav-btn {
        margin: 0 1;
        min-width: 12;
        height: 3;
        border: none;
        background: transparent;
        color: $text-muted;
    }

    NavBar .nav-btn:hover {
        background: $primary-darken-2;
        color: $text;
    }

    NavBar .nav-btn-primary {
        background: $success;
        color: $text;
    }

    NavBar .nav-btn-primary:hover {
        background: $success-darken-1;
    }

    /* Active state - the current page indicator */
    NavBar .nav-btn.active {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    NavBar .nav-btn.active:hover {
        background: $primary;
    }

    /* Primary button that is also active */
    NavBar .nav-btn-primary.active {
        background: $primary;
    }
    """

    def __init__(self, active: str = "home", **kwargs) -> None:
        super().__init__(**kwargs)
        self.active_page = active

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Logo section (left)
            yield Static(DOCTOWN_LOGO_COMPACT, classes="logo-section logo")

            # Spacer
            yield Static("", classes="nav-spacer")

            # Navigation section (right)
            # Buttons have can_focus=False to prevent focus-related highlighting issues
            with Horizontal(classes="nav-section"):
                yield Button("📚 Commons", id="nav-commons", classes="nav-btn")
                yield Button("⚡ Generate", id="nav-generate", classes="nav-btn nav-btn-primary")
                yield Button("🔍 Explore", id="nav-explore", classes="nav-btn")

    def on_mount(self) -> None:
        """Highlight the active nav button."""
        self._update_active()

    def _update_active(self) -> None:
        """Update which nav button appears active."""
        for btn in self.query(".nav-btn"):
            btn.remove_class("active")

        active_id = f"nav-{self.active_page}"
        try:
            active_btn = self.query_one(f"#{active_id}", Button)
            active_btn.add_class("active")
        except Exception:
            pass

    def set_active(self, page: str) -> None:
        """Set the active page."""
        self.active_page = page
        self._update_active()

    @on(Button.Pressed, ".nav-btn")
    def on_nav_pressed(self, event: Button.Pressed) -> None:
        """Handle navigation button clicks."""
        button_id = event.button.id or ""
        if button_id.startswith("nav-"):
            destination = button_id[4:]  # Remove "nav-" prefix
            # Blur the button to prevent focus highlighting from persisting
            event.button.blur()
            self.post_message(self.Navigate(destination))
