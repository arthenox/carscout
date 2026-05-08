#!/usr/bin/env python3
"""
CarScout - Professional OBD2 Diagnostic Tool
by arthenox

A free, open-source OBD2 diagnostic tool that works offline,
supports USB and Bluetooth ELM327 adapters, and includes a
local DTC database with thousands of trouble code descriptions.
"""

import argparse
import json
import os
import re
import sys
import time

try:
    import obd
except ImportError:
    print("Install python-obd: pip install obd")
    sys.exit(1)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

__version__ = "1.0.0"

# Base directory for resolving data file paths (BUG-6 fix)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------
# Demo mode mock data (Part 3: --demo feature)
# ----------------------------------------------------------------------
DEMO_DTC_CODES = [
    ("P0301", "Cylinder 1 Misfire Detected"),
    ("P0420", "Catalyst System Efficiency Below Threshold (Bank 1)"),
    ("P0171", "System Too Lean (Bank 1)"),
]

DEMO_LIVE_DATA = {
    "RPM": ("2500", "rpm"),
    "SPEED": ("80", "kph"),
    "COOLANT_TEMP": ("92", "degC"),
    "ENGINE_LOAD": ("45.2", "%"),
    "FUEL_LEVEL": ("72.0", "%"),
}

# ----------------------------------------------------------------------
# UI Language strings (EN/FR)
# ----------------------------------------------------------------------
LANGUAGES = {
    "en": {
        "app_name": "CarScout",
        "tagline": "Professional OBD2 Diagnostic Tool",
        "connecting": "Establishing connection to vehicle...",
        "connected": "Connection established successfully",
        "auto_failed": "Auto-detection failed. ELM327 not found.",
        "ask_port": "Enter serial port (e.g., /dev/ttyUSB0, COM3)"
                    " or press Enter to exit",
        "failed": "Connection failed. Please check the port"
                  " and try again.",
        "scanning": "Retrieving Diagnostic Trouble Codes (DTCs)...",
        "no_codes": "No trouble codes found. Engine is healthy.",
        "codes_found": "Found {count} trouble code(s):",
        "clear_confirm": "Are you sure you want to clear"
                         " all trouble codes?",
        "cleared": "All trouble codes have been cleared"
                   " successfully.",
        "cancelled": "Operation cancelled.",
        "live_data": "REAL-TIME SENSOR DATA",
        "to_stop": "Press Ctrl+C to stop streaming",
        "param": "Parameter",
        "value": "Value",
        "unit": "Unit",
        "no_valid_pids": "No valid PIDs responded from the ECU.",
        "menu_scan": "Scan Trouble Codes (DTCs)",
        "menu_clear": "Clear Trouble Codes",
        "menu_live": "Live Data Stream",
        "menu_exit": "Exit",
        "invalid_choice": "Invalid selection."
                          " Please choose 1, 2, 3, or 4.",
        "description": "Description",
        "goodbye": "Shutting down. Drive safely.",
        "na": "Not Available",
        "port_label": "Port",
        "press_enter": "Press Enter to continue...",
        "welcome": "Welcome to CarScout - a free,"
                   " open-source diagnostic tool.",
        "help_text": "Use the number keys to navigate.",
        "demo_mode": "DEMO MODE - Simulated data"
                     " (no real OBD2 connection)",
        "demo_connected": "Demo connection established"
                          " (simulated ELM327)",
    },
    "fr": {
        "app_name": "CarScout",
        "tagline": "Outil de diagnostic OBD2 professionnel",
        "connecting": "Connexion au vehicule en cours...",
        "connected": "Connexion etablie avec succes",
        "auto_failed": "Detection automatique echouee."
                       " ELM327 non trouve.",
        "ask_port": "Entrez le port serie"
                    " (ex: /dev/ttyUSB0) ou Entree pour quitter",
        "failed": "Echec de la connexion."
                  " Verifiez le port et reessayez.",
        "scanning": "Recuperation des codes d'erreur (DTC)...",
        "no_codes": "Aucun code d'erreur. Moteur sain.",
        "codes_found": "{count} code(s) d'erreur trouve(s) :",
        "clear_confirm": "Voulez-vous effacer tous les"
                         " codes d'erreur ?",
        "cleared": "Tous les codes d'erreur ont ete effaces.",
        "cancelled": "Operation annulee.",
        "live_data": "DONNEES CAPTEUR EN TEMPS REEL",
        "to_stop": "Appuyez sur Ctrl+C pour arreter",
        "param": "Parametre",
        "value": "Valeur",
        "unit": "Unite",
        "no_valid_pids": "Aucun PID valide n'a repondu.",
        "menu_scan": "Scanner les codes d'erreur",
        "menu_clear": "Effacer les codes d'erreur",
        "menu_live": "Flux de donnees en direct",
        "menu_exit": "Quitter",
        "invalid_choice": "Choix invalide."
                          " Veuillez entrer 1, 2, 3 ou 4.",
        "description": "Description",
        "goodbye": "Arret en cours. Conduisez prudemment.",
        "na": "Non disponible",
        "port_label": "Port",
        "press_enter": "Appuyez sur Entree pour continuer...",
        "welcome": "Bienvenue sur CarScout - outil de"
                   " diagnostic gratuit et open-source.",
        "help_text": "Utilisez les touches numeriques"
                     " pour naviguer.",
        "demo_mode": "MODE DEMO - Donnees simulees"
                     " (pas de connexion OBD2 reelle)",
        "demo_connected": "Connexion demo etablie"
                          " (ELM327 simule)",
    }
}


def get_text(key, lang="en"):
    """Return the localized string for the given key and language.

    Falls back to English if the key is not found in the
    requested language, and returns the key itself if not found
    in either language.

    Args:
        key: The translation key to look up.
        lang: Language code ('en' or 'fr'). Defaults to 'en'.

    Returns:
        The localized string, or the key if not found.
    """
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)


# ----------------------------------------------------------------------
# DTC Database loader
# ----------------------------------------------------------------------
def load_dtc_db(lang="en"):
    """Load the DTC description database for the specified language.

    Uses absolute paths (relative to this script's location) to ensure
    correct loading regardless of the working directory.

    Args:
        lang: Language code ('en' or 'fr'). Defaults to 'en'.

    Returns:
        A dictionary mapping DTC codes to their descriptions.
        Returns an empty dict if no database file is found.
    """
    if lang in ["en", "fr"]:
        db_file = os.path.join(BASE_DIR, f"dtc_db_{lang}.json")
    else:
        db_file = os.path.join(BASE_DIR, "dtc_db.json")

    if not os.path.exists(db_file):
        db_file = os.path.join(BASE_DIR, "dtc_db.json")
        if not os.path.exists(db_file):
            console.print(
                "[yellow]Warning: DTC database file not found.[/yellow]"
            )
            return {}

    try:
        with open(db_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print(
            "[bold red]Error: DTC database file is corrupted.[/bold red]"
        )
        return {}


# ----------------------------------------------------------------------
# Clean banner
# ----------------------------------------------------------------------
def show_banner(lang):
    """Display the CarScout application banner.

    Shows a styled panel with the application name, tagline, and
    author credit. The text is localized based on the given language.

    Args:
        lang: Language code ('en' or 'fr').
    """
    title_text = Text()
    title_text.append(" CarScout ", style="bold cyan on blue")
    title_text.append(" - ", style="dim")
    title_text.append(
        get_text("tagline", lang), style="italic bright_yellow"
    )
    subtitle = Text()
    subtitle.append("   Created by ", style="dim")
    subtitle.append("arthenox", style="bold magenta")
    subtitle.append(" | ", style="dim")
    subtitle.append("Offline DTC Database", style="dim green")
    panel = Panel(
        Text.assemble(title_text, "\n", subtitle),
        border_style="bright_blue",
        padding=(1, 2),
        expand=False
    )
    console.print()
    console.print(panel)
    console.print()


# ----------------------------------------------------------------------
# Connection
# ----------------------------------------------------------------------
def connect_to_car(lang, demo=False, delay=False):
    """Establish a connection to the vehicle via OBD2 adapter.

    In demo mode, returns a simulated connection object with
    mock data. In normal mode, attempts auto-detection first,
    then prompts for a manual port if auto-detection fails.

    Args:
        lang: Language code ('en' or 'fr').
        demo: If True, use simulated demo data instead of
            a real OBD2 connection.
        delay: If True, add artificial delays during connection
            (for visual effect). Defaults to False.

    Returns:
        An OBD connection object (real or simulated).
    """
    show_banner(lang)

    if demo:
        console.print(
            f"[bold cyan]{get_text('demo_mode', lang)}[/bold cyan]"
        )
        if delay:
            time.sleep(1.0)
        console.print(
            f"\n[bold green]"
            f"\u2713 {get_text('demo_connected', lang)}"
            f"[/bold green]\n"
        )
        return DemoConnection()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(
            description=f"[bold cyan]{get_text('connecting', lang)}",
            total=None
        )
        if delay:
            time.sleep(1.5)
        connection = obd.OBD()

    if connection.is_connected():
        console.print(
            f"\n[bold green]"
            f"\u2713 {get_text('connected', lang)}"
            f"[/bold green]"
        )
        console.print(
            f"[dim]   Port: {connection.port_name()}[/dim]\n"
        )
        return connection

    console.print(
        f"\n[bold red]"
        f"\u2717 {get_text('auto_failed', lang)}"
        f"[/bold red]\n"
    )

    try:
        port = Prompt.ask(
            f"[bold yellow]{get_text('ask_port', lang)}[/bold yellow]",
            default=""
        )
    except (KeyboardInterrupt, EOFError):
        console.print(f"\n[dim]{get_text('cancelled', lang)}[/dim]")
        sys.exit(0)

    if not port:
        sys.exit(0)

    # Validate serial port format (C-02: restrict to safe ports)
    PORT_PATTERN = re.compile(
        r'^(/dev/tty(USB|ACM|OBD)\d+|/dev/rfcomm\d+|COM\d+)$'
    )
    if not PORT_PATTERN.match(port):
        console.print(
            "[bold red]Invalid port format. "
            "Expected: /dev/ttyUSB0, /dev/ttyACM0, "
            "/dev/ttyOBD0, COM3, /dev/rfcomm0[/bold red]"
        )
        sys.exit(1)

    console.print(
        f"  [dim]{get_text('port_label', lang)}:[/dim]"
        f" [bold white]{port}[/bold white]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(
            description=f"[bold cyan]{get_text('connecting', lang)}",
            total=None
        )
        if delay:
            time.sleep(1.0)
        connection = obd.OBD(portstr=port)

    if connection.is_connected():
        console.print(
            f"\n[bold green]"
            f"\u2713 {get_text('connected', lang)}"
            f"[/bold green]"
        )
        console.print(
            f"[dim]   Port: {connection.port_name()}[/dim]\n"
        )
        return connection

    console.print(
        f"\n[bold red]"
        f"\u2717 {get_text('failed', lang)}"
        f"[/bold red]\n"
    )
    sys.exit(1)


# ----------------------------------------------------------------------
# Demo Connection class (--demo mode)
# ----------------------------------------------------------------------
class DemoConnection:
    """Simulated OBD2 connection for demo/testing mode.

    Provides mock responses for DTC scanning, clearing, and
    live data streaming without requiring real hardware.
    Supports simulate_failure mode for testing error handling.

    Attributes:
        dtc_codes: List of (code, description) tuples simulating
            stored diagnostic trouble codes.
        _simulate_failure: If True, simulates a disconnected
            or failing adapter (C-06).
    """

    def __init__(self, simulate_failure=False):
        """Initialize with default demo DTC codes.

        Args:
            simulate_failure: If True, is_connected() returns
                False and query() returns null responses.
        """
        self.dtc_codes = list(DEMO_DTC_CODES)
        self._simulate_failure = simulate_failure

    def is_connected(self):
        """Return True unless simulate_failure is set."""
        return not self._simulate_failure

    def port_name(self):
        """Return a simulated port name."""
        return "DEMO-MOCK"

    def query(self, command):
        """Return a mock response for the given OBD command.

        Args:
            command: An OBD command object or the GET_DTC constant.

        Returns:
            A MockResponse object with simulated data.
        """
        cmd_name = str(command)

        if cmd_name == "GET_DTC":
            codes = [(c, "") for c, _ in self.dtc_codes]
            return MockResponse(codes)

        if cmd_name == "CLEAR_DTC":
            self.dtc_codes = []
            return MockResponse(None)

        # Live data PIDs - exact match only (C-01)
        for pid, (val, unit) in DEMO_LIVE_DATA.items():
            if cmd_name == pid:
                return MockResponse(val, unit=unit)

        return MockResponse(None)

    def clear_demo_dtcs(self):
        """Clear the demo DTC codes list."""
        self.dtc_codes = []


class MockResponse:
    """Mock OBD response for demo mode.

    Wraps simulated data to match the interface of
    python-obd's OBDResponse class.

    Args:
        value: The response value (could be a list of DTC codes,
            a string reading, or None).
        unit: The unit string for the measurement (e.g., 'rpm').
    """

    def __init__(self, value, unit=""):
        """Initialize with the given value and unit."""
        self.value = value
        self._unit = unit

    @property
    def unit(self):
        """Return the unit string for this response."""
        return self._unit

    def is_null(self):
        """Check if the response value is None or empty."""
        return self.value is None or self.value == []


# ----------------------------------------------------------------------
# Scan DTCs
# ----------------------------------------------------------------------
def scan_dtcs(connection, lang, db):
    """Scan and display Diagnostic Trouble Codes from the vehicle.

    Queries the vehicle's ECU for stored DTCs and displays them
    in a formatted table with descriptions from the local database.

    Args:
        connection: An OBD connection object (real or demo).
        lang: Language code ('en' or 'fr').
        db: DTC description database dictionary.
    """
    if not db:
        db = {}

    console.print(f"[cyan]\u25ba {get_text('scanning', lang)}[/cyan]")
    response = connection.query(obd.commands.GET_DTC)
    codes = response.value if not response.is_null() else []

    if not codes:
        console.print(
            f"[bold green]"
            f"\u2713 {get_text('no_codes', lang)}"
            f"[/bold green]"
        )
        return

    console.print(
        f"[bold red]"
        f"\u26a0 {get_text('codes_found', lang).format(count=len(codes))}"
        f"[/bold red]"
    )

    table = Table(
        box=box.ROUNDED, show_header=True, header_style="bold magenta"
    )
    table.add_column(
        "Code", style="bold yellow", justify="center", width=10
    )
    table.add_column(get_text("description", lang), style="white")

    for code in codes:
        code_str = str(code[0]) if isinstance(code, tuple) else str(code)
        desc = db.get(code_str.upper(), get_text("na", lang))
        table.add_row(code_str, desc)

    console.print(table)
    console.print()


# ----------------------------------------------------------------------
# Clear DTCs
# ----------------------------------------------------------------------
def clear_dtcs(connection, lang):
    """Clear all stored Diagnostic Trouble Codes from the vehicle.

    Prompts the user for confirmation before sending the clear
    command to the ECU.

    Args:
        connection: An OBD connection object (real or demo).
        lang: Language code ('en' or 'fr').
    """
    if Confirm.ask(
        f"[bold red]{get_text('clear_confirm', lang)}[/bold red]"
    ):
        connection.query(obd.commands.CLEAR_DTC)
        # Verify DTCs were actually cleared (C-04)
        verify = connection.query(obd.commands.GET_DTC)
        if not verify.is_null() and verify.value:
            console.print(
                "[bold yellow]Warning: Some codes could not be "
                "cleared. They may be permanent DTCs.[/bold yellow]"
            )
        else:
            console.print(
                f"[bold green]"
                f"\u2713 {get_text('cleared', lang)}"
                f"[/bold green]"
            )
    else:
        console.print(
            f"[yellow]{get_text('cancelled', lang)}[/yellow]"
        )
    console.print()


# ----------------------------------------------------------------------
# Live Data
# ----------------------------------------------------------------------
def live_data(connection, pids, interval, lang):
    """Display real-time sensor data from the vehicle.

    Continuously queries the specified PIDs and displays their
    values in a refreshing table until the user presses Ctrl+C.

    Args:
        connection: An OBD connection object (real or demo).
        pids: List of PID names to query
            (e.g., ['RPM', 'SPEED', 'COOLANT_TEMP']).
        interval: Update interval in seconds.
        lang: Language code ('en' or 'fr').
    """
    console.print(
        Panel(
            f"[bold white on blue]"
            f"  {get_text('live_data', lang)}  "
            f"[/bold white on blue]",
            expand=False
        )
    )
    console.print(f"[dim]{get_text('to_stop', lang)}[/dim]\n")

    valid = []
    for pid in pids:
        cmd = getattr(obd.commands, pid.upper(), None)
        if cmd:
            valid.append(cmd)
        elif isinstance(connection, DemoConnection):
            valid.append(pid)

    if not valid:
        console.print(
            f"[yellow]{get_text('no_valid_pids', lang)}[/yellow]"
        )
        return

    try:
        while True:
            console.clear()
            console.print(
                Panel(
                    f"[bold white on blue]"
                    f"  {get_text('live_data', lang)}  "
                    f"[/bold white on blue]",
                    expand=False
                )
            )
            console.print(
                f"[dim]{get_text('to_stop', lang)}[/dim]\n"
            )

            table = Table(
                box=box.SIMPLE,
                show_header=True,
                header_style="bold green"
            )
            table.add_column(
                get_text("param", lang), style="bold cyan"
            )
            table.add_column(
                get_text("value", lang),
                justify="right",
                style="bold white"
            )
            table.add_column(
                get_text("unit", lang), style="dim"
            )

            null_count = 0  # (C-07) track empty responses
            for cmd in valid:
                if isinstance(connection, DemoConnection):
                    pid_name = (
                        cmd if isinstance(cmd, str) else cmd.name
                    )
                    pid_upper = pid_name.upper()
                    if pid_upper in DEMO_LIVE_DATA:
                        val, unit = DEMO_LIVE_DATA[pid_upper]
                        table.add_row(pid_name, val, unit)
                    else:
                        table.add_row(pid_name, "N/A", "")
                        null_count += 1
                else:
                    val = connection.query(cmd)
                    if not val.is_null():
                        table.add_row(
                            cmd.name, str(val.value),
                            str(cmd.unit)
                        )
                    else:
                        table.add_row(
                            cmd.name, "N/A", str(cmd.unit)
                        )
                        null_count += 1

            # (C-07) exit if all PIDs returned null
            if null_count == len(valid) and len(valid) > 0:
                console.print(table)
                console.print(
                    f"\n[yellow]{get_text('no_valid_pids', lang)}"
                    f"[/yellow]"
                )
                return

            console.print(table)
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print(
            f"\n[dim]{get_text('to_stop', lang)}[/dim]"
        )


# ----------------------------------------------------------------------
# Interactive Menu
# ----------------------------------------------------------------------
def menu_loop(connection, lang, db):
    """Run the interactive menu loop for CarScout.

    Displays the main menu and handles user selections for
    scanning DTCs, clearing DTCs, viewing live data, or exiting.

    Args:
        connection: An OBD connection object (real or demo).
        lang: Language code ('en' or 'fr').
        db: DTC description database dictionary.
    """
    console.print(
        Panel(
            f"[bold white]{get_text('welcome', lang)}[/bold white]",
            border_style="bright_blue",
            expand=False
        )
    )
    console.print(f"[dim]{get_text('help_text', lang)}[/dim]\n")

    # (C-03) check for interactive terminal
    if not sys.stdin.isatty():
        console.print(
            "[bold red]Interactive menu requires a terminal. "
            "Use subcommands: scan, clear, live.[/bold red]"
        )
        return

    while True:
        menu_panel = Panel(
            "\n".join([
                f"  [bold yellow]1[/bold yellow]"
                f"   {get_text('menu_scan', lang)}",
                f"  [bold yellow]2[/bold yellow]"
                f"   {get_text('menu_clear', lang)}",
                f"  [bold yellow]3[/bold yellow]"
                f"   {get_text('menu_live', lang)}",
                f"  [bold yellow]4[/bold yellow]"
                f"   {get_text('menu_exit', lang)}"
            ]),
            title=f"[bold white]{get_text('app_name', lang)}[/bold white]",
            subtitle="[bold magenta]by arthenox[/bold magenta]",
            border_style="bright_blue",
            padding=(1, 4)
        )
        console.print(menu_panel)

        choice = Prompt.ask(
            "[bold yellow]Your choice[/bold yellow]",
            choices=["1", "2", "3", "4"],
            default="1"
        )

        if choice == "1":
            scan_dtcs(connection, lang, db)
            Prompt.ask(
                f"[dim]{get_text('press_enter', lang)}[/dim]",
                default=""
            )

        elif choice == "2":
            clear_dtcs(connection, lang)
            Prompt.ask(
                f"[dim]{get_text('press_enter', lang)}[/dim]",
                default=""
            )

        elif choice == "3":
            live_data(
                connection,
                ["RPM", "SPEED", "COOLANT_TEMP",
                 "ENGINE_LOAD", "FUEL_LEVEL"],
                1.0,
                lang
            )

        elif choice == "4":
            console.print(
                f"[bold green]{get_text('goodbye', lang)}[/bold green]"
            )
            break


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    """Parse command-line arguments and run CarScout.

    Supports subcommands (scan, clear, live, menu) and options
    for language, PIDs, update interval, demo mode, and
    connection delay.
    """
    parser = argparse.ArgumentParser(
        description="CarScout - OBD2 Diagnostic Tool"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="menu",
        choices=["scan", "clear", "live", "menu"],
        help="Command to run"
    )
    # (C-05) add --version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"CarScout {__version__}"
    )
    parser.add_argument(
        "--lang",
        default="en",
        choices=["en", "fr"],
        help="Language (en/fr)"
    )
    parser.add_argument(
        "--pids",
        nargs="+",
        default=["RPM", "SPEED", "COOLANT_TEMP"],
        help="Live data PIDs"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Live data update interval"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with simulated data"
    )
    parser.add_argument(
        "--delay",
        action="store_true",
        help="Add artificial delays during connection"
    )
    args = parser.parse_args()

    # Validate --interval must be positive (C-03)
    if args.interval <= 0:
        parser.error("--interval must be a positive number")

    dtc_db = load_dtc_db(args.lang)
    conn = connect_to_car(
        args.lang, demo=args.demo, delay=args.delay
    )

    if args.command == "menu":
        menu_loop(conn, args.lang, dtc_db)
    elif args.command == "scan":
        scan_dtcs(conn, args.lang, dtc_db)
    elif args.command == "clear":
        clear_dtcs(conn, args.lang)
    elif args.command == "live":
        live_data(conn, args.pids, args.interval, args.lang)


if __name__ == "__main__":
    main()
