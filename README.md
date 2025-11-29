# Username Checker

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Release](https://img.shields.io/badge/Release-1.0.0-brightgreen.svg)
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

3. (Optional) Configure proxies:
Create a `proxies.txt` file in the root directory with one proxy per line:
```
ip:port:user:pass
ip:port:user:pass
```

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
├── .gitignore             # Git ignore rules
├── config/
│   ├── settings.json      # Configuration file
│   └── settings.py        # Settings manager
├── core/
│   ├── engine.py          # Main checking engine
│   ├── platforms.py       # Platform-specific checkers
│   └── validation.py      # Username validation rules
├── gui/
│   ├── main_window.py     # Main application window
│   └── components.py      # UI components
├── exports/               # Exported results directory
└── logs/                  # Application logs directory
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