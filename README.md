```bash
cat > README.md << 'EOF'
# CarScout 🔧

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OBD2](https://img.shields.io/badge/OBD2-ELM327-red)](https://www.elmelectronics.com/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20Termux-lightgrey)]()

> **CarScout** is a free, open‑source OBD2 diagnostic tool that works offline, supports USB and Bluetooth ELM327 adapters, and includes a local DTC database with thousands of trouble code descriptions.

## ✨ Features

- **Read & clear DTCs** – get detailed explanations (English/French) without internet.
- **Live sensor data** – monitor RPM, speed, coolant temperature, engine load, and more.
- **Offline first** – all DTC descriptions are stored locally – no cloud required.
- **Rich terminal UI** – colors, tables, progress bars, and intuitive menus.
- **Multi‑platform** – works on Linux, Windows, and even Android (Termux).
- **Open source** – MIT license, contributions welcome.

## 🎥 Demo

![CarScout Demo](carscout_demo.gif)

> *The GIF above shows scanning and clearing trouble codes.*

## 📦 Installation

```bash
git clone https://github.com/arthenox/carscout.git
cd carscout
pip install -r requirements.txt
```

ℹ️ Note for Linux / Termux: you may need to install python3-venv or use a virtual environment.

🚀 Usage

Interactive menu (recommended)

```bash
python carscout.py
```

Quick commands

```bash
# Scan trouble codes
python carscout.py scan

# Clear trouble codes
python carscout.py clear

# Live data stream
python carscout.py live

# French interface
python carscout.py --lang fr
```

Command line options

Option Description
--lang {en,fr} Interface language (default: en)
--pids Custom PIDs for live data (e.g., RPM SPEED)
--interval Live data update interval in seconds

🧰 Requirements

· Python 3.7+
· ELM327 adapter (USB or Bluetooth)
· OBD2 compatible car (1996+ US, 2001+ EU)

🤝 Contributing

Contributions, issues, and feature requests are welcome!
See CONTRIBUTING.md for guidelines.

📜 License

Distributed under the MIT License. See LICENSE for more information.

⚠️ Disclaimer

Use this tool only on vehicles you own or have explicit permission to test. The author is not responsible for any misuse or damage.

💬 Contact & Support

· Author: arthenox
· Issues: GitHub Issues

---

Made with 🚗 and Python
EOF

```

---
