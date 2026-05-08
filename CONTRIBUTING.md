# Contributing to CarScout

First off, thank you for considering contributing to CarScout! It is people like you who make CarScout a great tool for the OBD2 diagnostic community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Testing](#testing)

## Code of Conduct

This project and everyone participating in it is governed by the [CarScout Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to arthenox@proton.me.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title** for the issue.
- **Describe the exact steps to reproduce the problem** in as much detail as possible.
- **Provide specific examples** to demonstrate the steps (e.g., the exact command you ran).
- **Describe the behavior you observed** and what behavior you expected instead.
- **Include your environment details**: OS, Python version, ELM327 adapter type (USB/Bluetooth), and connection method.
- **Include relevant logs or screenshots** if applicable.

You can use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) to ensure all necessary information is included.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title** for the issue.
- **Provide a step-by-step description** of the suggested enhancement.
- **Provide specific examples** to demonstrate how the feature would be used.
- **Describe the current behavior** and explain the expected behavior.
- **Explain why this enhancement would be useful** to most CarScout users.
- **List some other OBD2 tools** that have this feature, if applicable.

You can use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) to structure your suggestion.

### Pull Requests

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** in a new git branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Follow coding standards** (see below).
4. **Write or update tests** for your changes.
5. **Ensure all tests pass** before submitting:
   ```bash
   python -m pytest tests/ -v
   ```
6. **Commit your changes** using a descriptive commit message.
7. **Push your branch** to your fork:
   ```bash
   git push origin feature/my-new-feature
   ```
8. **Open a Pull Request** against the `main` branch.

Fill in the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) to provide context for your changes.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arthenox/carscout.git
   cd carscout
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest flake8  # Dev dependencies
   ```

4. **Run in demo mode** to test without hardware:
   ```bash
   python carscout.py --demo
   ```

5. **Run the test suite**:
   ```bash
   python -m pytest tests/ -v
   ```

## Coding Standards

- **Follow PEP 8** style guidelines for Python code.
- **Use meaningful variable names** that describe the purpose of the variable.
- **Add docstrings** to all functions, classes, and modules following the Google or NumPy style.
- **Keep functions focused** — each function should do one thing well.
- **Maintain compatibility** with Python 3.9+ (no walrus operators or other 3.10+ features).
- **Run flake8** before committing to ensure zero linting errors:
  ```bash
  flake8 carscout.py --max-line-length=88
  ```
- **Support both languages**: if you add user-facing strings, add them to both `LANGUAGES["en"]` and `LANGUAGES["fr"]` in `carscout.py`.

## Commit Messages

- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or fewer.
- Reference issues and pull requests liberally after the first line.
- Consider starting your commit message with an applicable emoji:
  - 🐛 `:bug:` — Bug fix
  - ✨ `:sparkles:` — New feature
  - 📝 `:memo:` — Documentation
  - 🧪 `:test_tube:` — Tests
  - ♻️ `:recycle:` — Refactoring
  - 🔧 `:wrench:` — Configuration
  - 💬 `:speech_balloon:` — Localization/i18n

## Testing

All contributions should include appropriate tests. The test suite uses **pytest** and currently includes 34 passing tests.

- **Run the full test suite**:
  ```bash
  python -m pytest tests/ -v
  ```

- **Run a specific test class**:
  ```bash
  python -m pytest tests/test_carscout.py::TestDemoConnection -v
  ```

- **Check test coverage** (optional):
  ```bash
  pip install pytest-cov
  python -m pytest tests/ --cov=carscout --cov-report=term-missing
  ```

- **Test demo mode manually** to verify the UI works as expected:
  ```bash
  python carscout.py --demo
  python carscout.py --demo --lang fr
  ```

Thank you for your contributions! Every pull request, bug report, and feature suggestion helps make CarScout better for everyone.
