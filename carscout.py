#!/usr/bin/env python3
"""
CarScout - Professional OBD2 Diagnostic Tool
by arthenox
"""

import argparse
import json
import os
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
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

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
        "ask_port": "Enter serial port (e.g., /dev/ttyUSB0, COM3) or press Enter to exit",
        "failed": "Connection failed. Please check the port and try again.",
        "scanning": "Retrieving Diagnostic Trouble Codes (DTCs)...",
        "no_codes": "No trouble codes found. Engine is healthy.",
        "codes_found": "Found {count} trouble code(s):",
        "clear_confirm": "Are you sure you want to clear all trouble codes?",
        "cleared": "All trouble codes have been cleared successfully.",
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
        "invalid_choice": "Invalid selection. Please choose 1, 2, 3, or 4.",
        "description": "Description",
        "goodbye": "Shutting down. Drive safely.",
        "na": "Not Available",
        "port_label": "Port",
        "press_enter": "Press Enter to continue...",
        "welcome": "Welcome to CarScout – a free, open-source diagnostic tool.",
        "help_text": "Use the number keys to navigate."
    },
    "fr": {
        "app_name": "CarScout",
        "tagline": "Outil de diagnostic OBD2 professionnel",
        "connecting": "Connexion au véhicule en cours...",
        "connected": "Connexion établie avec succès",
        "auto_failed": "Détection automatique échouée. ELM327 non trouvé.",
        "ask_port": "Entrez le port série (ex: /dev/ttyUSB0) ou Entrée pour quitter",
        "failed": "Échec de la connexion. Vérifiez le port et réessayez.",
        "scanning": "Récupération des codes d'erreur (DTC)...",
        "no_codes": "Aucun code d'erreur. Moteur sain.",
        "codes_found": "{count} code(s) d'erreur trouvé(s) :",
        "clear_confirm": "Voulez-vous effacer tous les codes d'erreur ?",
        "cleared": "Tous les codes d'erreur ont été effacés.",
        "cancelled": "Opération annulée.",
        "live_data": "DONNÉES CAPTEUR EN TEMPS RÉEL",
        "to_stop": "Appuyez sur Ctrl+C pour arrêter",
        "param": "Paramètre",
        "value": "Valeur",
        "unit": "Unité",
        "no_valid_pids": "Aucun PID valide n'a répondu.",
        "menu_scan": "Scanner les codes d'erreur",
        "menu_clear": "Effacer les codes d'erreur",
        "menu_live": "Flux de données en direct",
        "menu_exit": "Quitter",
        "invalid_choice": "Choix invalide. Veuillez entrer 1, 2, 3 ou 4.",
        "description": "Description",
        "goodbye": "Arrêt en cours. Conduisez prudemment.",
        "na": "Non disponible",
        "port_label": "Port",
        "press_enter": "Appuyez sur Entrée pour continuer...",
        "welcome": "Bienvenue sur CarScout – outil de diagnostic gratuit et open-source.",
        "help_text": "Utilisez les touches numériques pour naviguer."
    }
}

def get_text(key, lang="en"):
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)

# ----------------------------------------------------------------------
# DTC Database loader
# ----------------------------------------------------------------------
def load_dtc_db(lang="en"):
    db_file = f"dtc_db_{lang}.json" if lang in ["en", "fr"] else "dtc_db.json"
    if not os.path.exists(db_file):
        db_file = "dtc_db.json"
        if not os.path.exists(db_file):
            console.print("[yellow]Warning: DTC database file not found.[/yellow]")
            return {}
    with open(db_file, "r", encoding="utf-8") as f:
        return json.load(f)

# ----------------------------------------------------------------------
# Clean banner
# ----------------------------------------------------------------------
def show_banner(lang):
    title_text = Text()
    title_text.append(" CarScout ", style="bold cyan on blue")
    title_text.append(" - ", style="dim")
    title_text.append(get_text("tagline", lang), style="italic bright_yellow")
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
def connect_to_car(lang):
    show_banner(lang)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=f"[bold cyan]{get_text('connecting', lang)}", total=None)
        time.sleep(1.5)
        connection = obd.OBD()
    if connection.is_connected():
        console.print(f"\n[bold green]✓ {get_text('connected', lang)}[/bold green]")
        console.print(f"[dim]   Port: {connection.port_name()}[/dim]\n")
        return connection
    console.print(f"\n[bold red]✗ {get_text('auto_failed', lang)}[/bold red]\n")
    try:
        port = Prompt.ask(f"[bold yellow]{get_text('ask_port', lang)}[/bold yellow]", default="")
    except (KeyboardInterrupt, EOFError):
        console.print(f"\n[dim]{get_text('cancelled', lang)}[/dim]")
        sys.exit(0)
    if not port:
        sys.exit(0)
    console.print(f"  [dim]{get_text('port_label', lang)}:[/dim] [bold white]{port}[/bold white]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=f"[bold cyan]{get_text('connecting', lang)}", total=None)
        time.sleep(1)
        connection = obd.OBD(portstr=port)
    if connection.is_connected():
        console.print(f"\n[bold green]✓ {get_text('connected', lang)}[/bold green]")
        console.print(f"[dim]   Port: {connection.port_name()}[/dim]\n")
        return connection
    console.print(f"\n[bold red]✗ {get_text('failed', lang)}[/bold red]\n")
    sys.exit(1)

# ----------------------------------------------------------------------
# Scan DTCs
# ----------------------------------------------------------------------
def scan_dtcs(connection, lang, db):
    console.print(f"[cyan]► {get_text('scanning', lang)}[/cyan]")
    response = connection.query(obd.commands.GET_DTC)
    codes = response.value if not response.is_null() else []
    if not codes:
        console.print(f"[bold green]✓ {get_text('no_codes', lang)}[/bold green]")
        return
    console.print(f"[bold red]⚠ {get_text('codes_found', lang).format(count=len(codes))}[/bold red]")
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Code", style="bold yellow", justify="center", width=10)
    table.add_column(get_text("description", lang), style="white")
    for code in codes:
        desc = db.get(str(code).upper(), get_text("na", lang))
        table.add_row(str(code), desc)
    console.print(table)
    console.print()

# ----------------------------------------------------------------------
# Clear DTCs
# ----------------------------------------------------------------------
def clear_dtcs(connection, lang):
    if Confirm.ask(f"[bold red]{get_text('clear_confirm', lang)}[/bold red]"):
        connection.query(obd.commands.CLEAR_DTC)
        console.print(f"[bold green]✓ {get_text('cleared', lang)}[/bold green]")
    else:
        console.print(f"[yellow]{get_text('cancelled', lang)}[/yellow]")
    console.print()

# ----------------------------------------------------------------------
# Live Data – stable version without rich.Live
# ----------------------------------------------------------------------
def live_data(connection, pids, interval, lang):
    console.print(Panel(f"[bold white on blue]  {get_text('live_data', lang)}  [/bold white on blue]", expand=False))
    console.print(f"[dim]{get_text('to_stop', lang)}[/dim]\n")
    valid = []
    for pid in pids:
        cmd = getattr(obd.commands, pid.upper(), None)
        if cmd:
            valid.append(cmd)
    if not valid:
        console.print(f"[yellow]{get_text('no_valid_pids', lang)}[/yellow]")
        return
    try:
        while True:
            console.clear()
            console.print(Panel(f"[bold white on blue]  {get_text('live_data', lang)}  [/bold white on blue]", expand=False))
            console.print(f"[dim]{get_text('to_stop', lang)}[/dim]\n")
            table = Table(box=box.SIMPLE, show_header=True, header_style="bold green")
            table.add_column(get_text("param", lang), style="bold cyan")
            table.add_column(get_text("value", lang), justify="right", style="bold white")
            table.add_column(get_text("unit", lang), style="dim")
            for cmd in valid:
                val = connection.query(cmd)
                if not val.is_null():
                    table.add_row(cmd.name, str(val.value), str(cmd.unit))
                else:
                    table.add_row(cmd.name, "N/A", str(cmd.unit))
            console.print(table)
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print(f"\n[dim]{get_text('to_stop', lang)}[/dim]")

# ----------------------------------------------------------------------
# Interactive Menu
# ----------------------------------------------------------------------
def menu_loop(connection, lang, db):
    console.print(Panel(f"[bold white]{get_text('welcome', lang)}[/bold white]", border_style="bright_blue", expand=False))
    console.print(f"[dim]{get_text('help_text', lang)}[/dim]\n")
    while True:
        menu_panel = Panel(
            "\n".join([
                f"  [bold yellow]1[/bold yellow]   {get_text('menu_scan', lang)}",
                f"  [bold yellow]2[/bold yellow]   {get_text('menu_clear', lang)}",
                f"  [bold yellow]3[/bold yellow]   {get_text('menu_live', lang)}",
                f"  [bold yellow]4[/bold yellow]   {get_text('menu_exit', lang)}"
            ]),
            title=f"[bold white]{get_text('app_name', lang)}[/bold white]",
            subtitle="[bold magenta]by arthenox[/bold magenta]",
            border_style="bright_blue",
            padding=(1, 4)
        )
        console.print(menu_panel)
        choice = Prompt.ask("[bold yellow]Your choice[/bold yellow]", choices=["1", "2", "3", "4"], default="1")
        if choice == "1":
            scan_dtcs(connection, lang, db)
            input(f"[dim]{get_text('press_enter', lang)}[/dim]")
        elif choice == "2":
            clear_dtcs(connection, lang)
            input(f"[dim]{get_text('press_enter', lang)}[/dim]")
        elif choice == "3":
            live_data(connection, ["RPM", "SPEED", "COOLANT_TEMP"], 1.0, lang)
        elif choice == "4":
            console.print(f"[bold green]{get_text('goodbye', lang)}[/bold green]")
            break

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="CarScout - OBD2 Diagnostic Tool")
    parser.add_argument("command", nargs="?", default="menu", choices=["scan", "clear", "live", "menu"],
                        help="Command to run")
    parser.add_argument("--lang", default="en", choices=["en", "fr"], help="Language (en/fr)")
    parser.add_argument("--pids", nargs="+", default=["RPM", "SPEED", "COOLANT_TEMP"], help="Live data PIDs")
    parser.add_argument("--interval", type=float, default=1.0, help="Live data update interval")
    args = parser.parse_args()
    dtc_db = load_dtc_db(args.lang)
    if args.command == "menu":
        conn = connect_to_car(args.lang)
        menu_loop(conn, args.lang, dtc_db)
    else:
        conn = connect_to_car(args.lang)
        if args.command == "scan":
            scan_dtcs(conn, args.lang, dtc_db)
        elif args.command == "clear":
            clear_dtcs(conn, args.lang)
        elif args.command == "live":
            live_data(conn, args.pids, args.interval, args.lang)

if __name__ == "__main__":
    main()
