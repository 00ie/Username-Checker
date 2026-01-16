# Username Checker

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Release](https://img.shields.io/badge/Release-1.0.2-brightgreen.svg)
![Discord](https://img.shields.io/badge/Discord-Webhook-blueviolet.svg)

## Features

- **Bulk Username Checking**: Check hundreds of usernames across multiple platforms at once
- **Sniper Monitor**: Real-time monitoring of specific usernames to catch them when they become available
- **Multi-Platform Support**: Pinterest, Instagram, and GitHub integration
- **Discord Webhook Integration**: Get instant notifications when usernames become available
- **Proxy Support**: Built-in proxy rotation for rate limiting protection
- **Export Results**: Save available usernames to file for later use
- **Customizable Settings**: Adjust threads, timeouts, delays, and platform selection
- **Modern UI**: Clean, dark-themed interface built with Tkinter

## Supported Platforms

- Pinterest
- Instagram
- GitHub

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/methzzy/username-checker.git
cd username-checker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Note: the `requirements.txt` includes the `requests[socks]` extras so SOCKS proxies (socks5) are supported if your environment installs the extra dependencies (PySocks). If you prefer to install the SOCKS support separately run:
```bash
pip install requests[socks]
```

3. (Optional) Configure proxies:
Create a `proxies.txt` file in the root directory with one proxy per line. Supported formats:
```
host:port
user:pass@host:port
http://host:port
socks5://host:port
```

The app includes a builtin proxy manager and a GUI panel (Bulk tab) where you can add/remove proxies, run a check to validate them and clear the automatic blacklist. Proxies that fail checks are added to `bad_proxies.txt` (blacklist) and shown in the GUI in red.

4. (Optional) Configure Discord webhook:
Edit `config/settings.json` and add your webhook URL:
```json
{
    "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
}
```

## Usage

### Running the Application

```bash
python main.py
```

## Build do Executável (Windows)

Pré-requisitos:
- Python 3.8+ instalado no PATH
- Dependências do projeto instaladas

1) Instale as dependências e gere o executável (pasta `dist`):
```powershell
pip install -r requirements.txt
./scripts/build.ps1
```

2) Para gerar em pasta (onedir):
```powershell
./scripts/build.ps1 -Mode onedir
```

O executável estará em `dist/UsernameChecker.exe` (modo padrão `onefile`) ou em `dist/UsernameChecker/UsernameChecker.exe` (modo `onedir`).
No modo `onedir`, publique a **pasta inteira** `dist/UsernameChecker` — mover apenas o `.exe` causa erro de DLL.

### Bulk Checker

1. Select platforms to check from the sidebar
2. Set the number of usernames to generate and their length
3. Click "GENERATE LIST" to create random usernames
4. Click "START CHECKING" to begin the bulk check
5. Available usernames will be displayed in the console with green highlights
6. Export results using "EXPORT RESULTS" button

### Sniper Monitor

1. Switch to the "SNIPER MONITOR" tab
2. Enter the target username you want to monitor
3. Set check interval in seconds (default: 60)
4. Click "ACTIVATE SNIPER" to start monitoring
5. The tool will continuously check if the username becomes available
6. You'll receive Discord notifications (if configured) when it's available

## Configuration

Edit `config/settings.json` to customize:

```json
{
    "threads": 5,
    "timeout": 10,
    "webhook_url": "",
    "use_proxies": false,
    "jitter_min": 0.5,
    "jitter_max": 1.5,
    "platforms": {
        "instagram": true,
        "github": true,
        "pinterest": true
    }
}
```

### Configuration Options

- **threads**: Number of concurrent checking threads
- **timeout**: HTTP request timeout in seconds
- **webhook_url**: Discord webhook URL for notifications
- **use_proxies**: Enable/disable proxy rotation
- **jitter_min/max**: Random delay between requests (in seconds)
- **platforms**: Enable/disable specific platforms

## Project Structure

```
username-checker/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── config/
│   ├── settings.json       # Configuration file
│   └── settings.py         # Settings manager
├── core/
│   ├── engine.py           # Main checking engine
│   ├── platforms.py        # Platform-specific checkers
│   └── validation.py       # Username validation rules
├── gui/
│   ├── app_window.py       # Main application window
│   ├── window.py           # Alternate UI window
│   └── ui_kit.py            # UI helpers
├── themes python/
│   └── Sun-Valley-ttk-theme-main/
└── utils/
    └── ...
```

## Platform-Specific Rules

### Pinterest
- Length: 3-30 characters
- Allowed: letters, numbers, underscores
- Cannot be all numbers

### GitHub
- Max length: 39 characters
- Allowed: letters, numbers, hyphens
- Cannot start/end with hyphen
- No consecutive hyphens

### Instagram
- Max length: 30 characters
- Allowed: letters, numbers, periods, underscores
- Cannot start/end with period
- No consecutive periods

## Discord Webhook

When a username becomes available, you'll receive a Discord notification with:
- Username
- Platforms where it's available
- Direct links to claim
- Timestamp of discovery

## Changelog

### Version 1.0.0
- Initial release
- Multi-platform username checking
- Bulk checker with multi-threading
- Sniper monitor mode
- Discord webhook integration
- Proxy support
- Export functionality
- Modern dark UI

### Version 1.0.1
- Improved proxy management UI and features:
    - Dedicated "PROXIES" tab with a table (Proxy / Status).
    - Visual status column showing "BAD" for blacklisted proxies (red text).
    - Button to remove a single selected proxy (with confirmation).
    - Button to clear the blacklist (with confirmation).
    - New button "REMOVE BAD" to remove all blacklisted proxies from your proxy list at once (with confirmation).
    - Export button to write `good_proxies.txt` and `bad_proxies.txt` from the GUI.
    - Proxies are validated at application startup (background task) if `proxies.txt` exists.
    - Supports SOCKS proxies when `requests[socks]` (PySocks) is installed; SOCKS proxies will be auto-marked as bad if SOCKS support is missing.
    - Proxy checker now integrates with the blacklist automatically (bad proxies marked, good proxies unmarked).

## Version 1.0.2

- **UI polish**: Header/cards refined, labels standardized.
- **Performance**: Faster tab switching with lazy loading.
- **Settings**: Webhook and thread settings persist correctly.
- **Webhook**: Save/test flow improved and more reliable.
- **Shortcuts**: Added stop shortcut and improved tab hotkeys.

## Credits

- **Sun Valley ttk theme** by `rdbende` (MIT License): https://github.com/rdbende/sun-valley-ttk-theme
