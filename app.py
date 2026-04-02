"""PingBar macOS menu bar application.

This module contains the main application class for PingBar, a macOS menu bar
application that monitors network connectivity by pinging specified targets.
"""
from rumps import App, clicked, alert, notification, MenuItem, timer
from pinger import Pinger
from json import dump as json_dump, load as json_load
from icon import paused_icon, status_text


class PingBarApp(App):
    """Main application class for PingBar menu bar app.

    Extends the rumps.App class to provide a macOS menu bar application
    for network connectivity monitoring. Manages settings persistence
    and provides user interface controls for the pinger functionality.

    Attributes:
        pinger (Pinger): The network pinger instance.
        settings (dict): Application settings dictionary.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the PingBar application.

        Args:
            *args: Variable length argument list passed to parent App class.
            **kwargs: Arbitrary keyword arguments passed to parent App class.
        """
        super(PingBarApp, self).__init__(*args, **kwargs)
        self.settings = {}
        self._load_settings()
        self.latency = None
        self.loss = None
        self.icon = "pingbar.png"
        self.title = None

        self.statistics_menu = MenuItem("waiting...")
        self.menu = [self.statistics_menu, "Pause", "Preferences"]


    def _load_settings(self):
        """Load application settings from settings.json file.

        Attempts to load settings from the settings.json file. If the file
        doesn't exist or contains invalid JSON, default settings are used.
        """
        try:
            with self.open("settings.json", "r") as f:
                self.settings = json_load(f)
        except (IOError, ValueError):
            self.settings = {
                "paused": False,
                "targets": ["8.8.8.8", "1.1.1.1", "8.8.4.4", "1.0.0.1"],
            }
        self.pinger = Pinger(
            targets=self.settings.get("targets", []),
            start_running=not self.settings.get("paused", False),
            cb=self.update_statistics,
        )

    def _save_settings(self):
        """Save current application settings to settings.json file.

        Persists the current settings dictionary to the settings.json file
        in JSON format.
        """
        with self.open("settings.json", "w") as f:
            json_dump(self.settings, f)

    def set_setting(self, key, value):
        """Set a setting value and save to file.

        Args:
            key (str): The setting key to update.
            value: The value to set for the key.
        """
        self.settings[key] = value
        if key == "targets":
            self.pinger.targets = value
        if key == "paused":
            self.pinger.run(not value)

        self._save_settings()

    def get_setting(self, key, default=None):
        """Get a setting value.

        Args:
            key (str): The setting key to retrieve.
            default: Default value to return if key doesn't exist.

        Returns:
            The setting value or the default value if key doesn't exist.
        """
        return self.settings.get(key, default)

    def update_statistics(self, latency: float = None, loss: float = None):
        """Update the statistics menu item text.

        Args:
            latency (float): The average latency in milliseconds.
            loss (float): The packet loss percentage.
        """
        if latency is not None:
            self.latency = latency
        if loss is not None:
            self.loss = loss
        print(f"Updating statistics: loss={self.loss}, latency={self.latency}")
    
    @timer(1)
    def refresh_menu(self, _):
        """Refresh the statistics menu item text every second."""
        if self.settings.get("paused"):
            self.statistics_menu.title = "Paused"
            self._icon_nsimage = paused_icon()
        else:
            loss_str = f"{(self.loss*100):.2f}%" if self.loss is not None else "N/A"
            latency_str = f"{(self.latency):.2f} ms" if self.latency is not None else "N/A"
            self.statistics_menu.title = f"Loss: {loss_str}, Latency: {latency_str}"
            if self.loss is not None and self.latency is not None:
                self._icon_nsimage = status_text(self.latency, self.loss)
        self._nsapp.setStatusBarIcon()


    @clicked("Preferences")
    def prefs(self, _):
        """Handle preferences menu item click.

        Currently displays a placeholder alert. Future versions could
        open a preferences window.

        Args:
            _: Unused menu item parameter.
        """
        alert("jk! no preferences available!")

    @clicked("Pause")
    def onoff(self, sender):
        """Toggle the pinger on/off state.

        Toggles the menu item state and starts/stops the pinger accordingly.

        Args:
            sender: The menu item that was clicked.
        """
        self.set_setting("paused", not self.get_setting("paused", False))
        sender.state = self.get_setting("paused", False)

