# Changelog

All notable changes to CarScout will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-08

### Added

- Initial release of CarScout OBD2 Diagnostic Tool.
- Interactive menu with Rich-based terminal user interface.
- Scan Diagnostic Trouble Codes (DTCs) from vehicle ECU.
- Clear Diagnostic Trouble Codes with confirmation prompt.
- Live data streaming for real-time sensor monitoring (RPM, speed, coolant temperature, engine load, fuel level).
- Dual language support: English (`--lang en`) and French (`--lang fr`).
- Local offline DTC database with 2,972 trouble code descriptions per language.
- Demo mode (`--demo`) for testing without real OBD2 hardware.
- Connection delay simulation (`--delay`) for visual connection feedback.
- USB Serial and Bluetooth (ELM327) adapter support.
- Customizable live data PIDs (`--pids`) and update interval (`--interval`).
- Subcommands for non-interactive usage: `scan`, `clear`, `live`, `menu`.
- 34 unit tests covering core functionality, localization, and demo mode.
- GPL-2.0 License.

### Fixed

- **BUG-1**: Crash when `dtc_db_en.json` was missing — added graceful fallback with warning message.
- **BUG-2**: `obd.OBD()` called without arguments failed silently — improved auto-detection with manual port fallback.
- **BUG-3**: French database (`dtc_db_fr.json`) contained Portuguese entries — purged all Portuguese contamination from both EN and FR databases.
- **BUG-4**: `load_dtc_db()` used relative paths — switched to absolute paths based on script location (`BASE_DIR`).
- **BUG-5**: `live_data()` crashed when no valid PIDs responded — added validation and user-friendly error message.
- **BUG-6**: Database file paths were resolved relative to CWD instead of script directory — fixed with `os.path.dirname(os.path.abspath(__file__))`.
- **BUG-7**: `input()` calls inside Rich panels caused display corruption — replaced with proper `console.print()` + `input()` separation.
- **BUG-8**: `clear_dtcs()` lacked confirmation prompt — added `Confirm.ask()` before clearing codes.
- **BUG-9**: Demo mode `MockResponse` did not match the `python-obd` response interface — aligned `is_null()` and `value` attribute behavior.
- **BUG-10**: `--lang` argument accepted invalid values without error — added `choices=["en", "fr"]` constraint.
- **BUG-11**: `menu_loop()` did not handle `KeyboardInterrupt` gracefully — added try/except for clean exit on Ctrl+C.
- **BUG-12**: Missing `--demo` flag documentation and help text — added `argparse` help strings and README documentation.

### Changed

- Replaced basic `print()` output with Rich library for professional terminal UI (tables, panels, progress bars, spinners, colors).
- Improved connection flow with spinner animation and clear status messages.
- Enhanced DTC scan results table with rounded box drawing and color-coded entries.
- Localized all user-facing strings into the `LANGUAGES` dictionary for proper i18n support.

### Security

- No security vulnerabilities reported at release time.
- See [SECURITY.md](SECURITY.md) for vulnerability reporting guidelines.
