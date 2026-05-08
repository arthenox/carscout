# Security Policy

## Supported Versions

CarScout is currently in active development. Security updates are applied to the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of CarScout seriously. If you have discovered a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner.

### Please Do

- **Report vulnerabilities privately** by sending an email to: **arthenox@proton.me**
- Include a detailed description of the vulnerability, including the steps to reproduce it.
- Provide the affected version(s) and the relevant component or code path.
- If possible, suggest a fix or mitigation.
- Allow us a reasonable amount of time to respond and address the issue before public disclosure.

### Please Do Not

- Do not publicly disclose the vulnerability before a fix has been released.
- Do not exploit the vulnerability for any purpose other than verification.
- Do not access, modify, or delete other users' data.

### Response Timeline

We aim to respond to security reports within the following timeframes:

| Stage | Target Time |
|-------|-------------|
| Acknowledgment of report | Within 48 hours |
| Initial assessment and triage | Within 5 business days |
| Fix development and testing | Within 30 days (severity dependent) |
| Security advisory publication | After fix is released |

### Disclosure Policy

- Once a fix has been developed and released, we will publish a security advisory on GitHub Security Advisories.
- We will credit the reporter in the advisory unless they request anonymity.
- We kindly ask that you do not disclose the vulnerability publicly until the fix has been published.

### Security Considerations for CarScout

CarScout interacts with vehicle diagnostic systems via OBD2 adapters. Please be aware of the following:

- **Vehicle Safety**: CarScout is intended for diagnostic purposes only. Improper use of OBD2 clear commands or live data misinterpretation should not be used to make driving decisions.
- **Serial Port Access**: CarScout communicates with ELM327 adapters over serial ports (USB or Bluetooth). Ensure your serial port connections are secure and not exposed to unauthorized access.
- **Bluetooth Security**: When using Bluetooth ELM327 adapters, ensure your device pairing is configured with proper authentication to prevent unauthorized connections.
- **Data Privacy**: CarScout operates entirely offline. No vehicle data is transmitted to any external server or cloud service.

### Contact

For any security-related questions or concerns, contact: **arthenox@proton.me**

For general bug reports and feature requests, please use [GitHub Issues](https://github.com/arthenox/carscout/issues).
