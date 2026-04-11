#!/usr/bin/env python3
"""
CarScout - OBD2 Diagnostic Tool
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

console = Console()

# ----------------------------------------------------------------------
# UI Language strings (EN/FR) – no emojis
# ----------------------------------------------------------------------
LANGUAGES = {
    "en": {
        "app_name": "CarScout",
        "tagline": "Your Pocket Mechanic",
        "connecting": "Connecting to vehicle...",
        "connected": "Connected successfully!",
        "auto_failed": "Auto-detection failed. No ELM327 found.",
        "ask_port": "Please enter the serial port (e.g. /dev/ttyUSB0, COM3) or press Enter to quit",
        "failed": "Connection failed. Please check the port and try again.",
        "scanning": "Scanning ECU for trouble codes...",
        "no_codes": "No trouble codes found. Your engine is healthy.",
        "codes_found": "Found {count} trouble code(s):",
        "clear_confirm": "Are you sure you want to clear all trouble codes?",
        "cleared": "Trouble codes cleared successfully.",
        "cancelled": "Operation cancelled.",
        "live_data": "LIVE DATA STREAM",
        "to_stop": "Press Ctrl+C to stop",
        "param": "Parameter",
        "value": "Value",
        "unit": "Unit",
        "no_valid_pids": "No valid PIDs responded from the ECU.",
        "menu_scan": "[1] Scan Trouble Codes (DTCs)",
        "menu_clear": "[2] Clear Trouble Codes",
        "menu_live": "[3] Live Data Stream",
        "menu_exit": "[4] Exit",
        "invalid_choice": "Invalid option. Please choose 1, 2, 3, or 4.",
        "description": "Description",
        "goodbye": "Goodbye! Drive safely.",
        "na": "N/A",
        "port_label": "PORT",
        "press_enter": "Press Enter to continue...",
        "welcome": "Welcome to CarScout – the free, open-source OBD2 diagnostic tool.",
        "help_text": "Select an option using the number keys."
    },
    "fr": {
        "app_name": "CarScout",
        "tagline": "Votre Mecanicien de Poche",
        "connecting": "Connexion au vehicule...",
        "connected": "Connecte avec succes !",
        "auto_failed": "Detection automatique echouee. Aucun ELM327 trouve.",
        "ask_port": "Entrez le port serie (ex: /dev/ttyUSB0) ou Entree pour quitter",
        "failed": "Echec de la connexion. Verifiez le port et reessayez.",
        "scanning": "Analyse de l'ECU pour les codes d'erreur...",
        "no_codes": "Aucun code d'erreur. Votre moteur est sain.",
        "codes_found": "{count} code(s) d'erreur trouve(s) :",
        "clear_confirm": "Voulez-vous effacer tous les codes d'erreur ?",
        "cleared": "Codes d'erreur effaces avec succes.",
        "cancelled": "Operation annulee.",
        "live_data": "DONNEES EN DIRECT",
        "to_stop": "Appuyez sur Ctrl+C pour arreter",
        "param": "Parametre",
        "value": "Valeur",
        "unit": "Unite",
        "no_valid_pids": "Aucun PID valide n'a repondu de l'ECU.",
        "menu_scan": "[1] Scanner les codes d'erreur (DTCs)",
        "menu_clear": "[2] Effacer les codes d'erreur",
        "menu_live": "[3] Flux de donnees en direct",
        "menu_exit": "[4] Quitter",
        "invalid_choice": "Option invalide. Choisissez 1, 2, 3 ou 4.",
        "description": "Description",
        "goodbye": "Au revoir ! Conduisez prudemment.",
        "na": "N/D",
        "port_label": "PORT",
        "press_enter": "Appuyez sur Entree pour continuer...",
        "welcome": "Bienvenue sur CarScout – l'outil de diagnostic OBD2 gratuit et open-source.",
        "help_text": "Selectionnez une option a l'aide des touches numeriques."
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
# Banner without emojis
# ----------------------------------------------------------------------
def show_banner(lang):
    title = Text()
    title.append(" CarScout ", style="bold cyan")
    title.append(" - ", style="dim")
    title.append(get_text("tagline", lang), style="italic")
    subtitle = Text()
    subtitle.append("   Created by ", style="dim")
    subtitle.append("arthenox", style="bold magenta")
    subtitle.append(" | ", style="dim")
    subtitle.append("Offline DTC Database", style="dim green")
    panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="bright_blue",
        padding=(1, 2),
        expand=False
    )
    console.print()
    console.print(panel)
    console.print()

# ----------------------------------------------------------------------
# Connection with progress animation
# ----------------------------------------------------------------------
def connect_to_car(lang):
    show_banner(lang)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=get_text("connecting", lang), total=None)
        time.sleep(1.5)
        connection = obd.OBD()
    if connection.is_connected():
        console.print(f"\n[bold green]{get_text('connected', lang)}[/bold green]\n")
        return connection
    console.print(f"\n[bold red]{get_text('auto_failed', lang)}[/bold red]\n")
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
        progress.add_task(description=get_text("connecting", lang), total=None)
        time.sleep(1)
        connection = obd.OBD(portstr=port)
    if connection.is_connected():
        console.print(f"\n[bold green]{get_text('connected', lang)}[/bold green]\n")
        return connection
    console.print(f"\n[bold red]{get_text('failed', lang)}[/bold red]\n")
    sys.exit(1)

# ----------------------------------------------------------------------
# Scan DTCs
# ----------------------------------------------------------------------
def scan_dtcs(connection, lang, db):
    console.print(f"[cyan]{get_text('scanning', lang)}[/cyan]")
    codes = connection.query_codes()
    if not codes:
        console.print(f"[green]{get_text('no_codes', lang)}[/green]")
        return
    console.print(f"[bold red]{get_text('codes_found', lang).format(count=len(codes))}[/bold red]")
    table = Table(box=None, show_header=True, header_style="bold magenta")
    table.add_column("Code", style="bold yellow", justify="center", width=10)
    table.add_column(get_text("description", lang), style="white")
    for code in codes:
        desc = db.get(code.upper(), get_text("na", lang))
        table.add_row(str(code), desc)
    console.print(table)
    console.print()

# ----------------------------------------------------------------------
# Clear DTCs
# ----------------------------------------------------------------------
def clear_dtcs(connection, lang):
    if Confirm.ask(f"[bold red]{get_text('clear_confirm', lang)}[/bold red]"):
        connection.clear_dtc()
        console.print(f"[green]{get_text('cleared', lang)}[/green]")
    else:
        console.print(f"[yellow]{get_text('cancelled', lang)}[/yellow]")
    console.print()

# ----------------------------------------------------------------------
# Live Data
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
    table = Table(box=None, show_header=True, header_style="bold green")
    table.add_column(get_text("param", lang), style="bold cyan")
    table.add_column(get_text("value", lang), justify="right", style="bold white")
    table.add_column(get_text("unit", lang), style="dim")
    try:
        with Live(table, console=console, refresh_per_second=10) as live:
            while True:
                table.rows.clear()
                for cmd in valid:
                    val = connection.query(cmd)
                    if not val.is_null():
                        table.add_row(cmd.name, str(val.value), str(cmd.unit))
                    else:
                        table.add_row(cmd.name, "N/A", str(cmd.unit))
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
                f"  {get_text('menu_scan', lang)}",
                f"  {get_text('menu_clear', lang)}",
                f"  {get_text('menu_live', lang)}",
                f"  {get_text('menu_exit', lang)}"
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
