# 🔖 Chromium Bookmark Manager

A powerful command-line tool for managing bookmarks in Chromium-based browsers on **macOS** using ScriptingBridge.

> **Direct manipulation** of bookmarks without import/export — changes appear instantly in your browser!

## ✨ Features

- 📋 **List** all bookmarks with customizable depth
- 🔍 **Search** bookmarks by title or URL
- ➕ **Add** bookmarks to any folder
- 📁 **Create** new bookmark folders
- 🗑️ **Delete** bookmarks or folders
- 🌐 **Multi-browser support** — works with 8+ Chromium browsers

## 🌐 Supported Browsers

| Browser | Key | Bundle ID |
|---------|-----|-----------|
| Google Chrome | `chrome` | `com.google.Chrome` |
| Brave | `brave` | `com.brave.Browser` |
| Microsoft Edge | `edge` | `com.microsoft.edgemac` |
| Arc | `arc` | `company.thebrowser.Browser` |
| Vivaldi | `vivaldi` | `com.vivaldi.Vivaldi` |
| Comet (Perplexity) | `comet` | `ai.perplexity.comet` |
| Opera | `opera` | `com.operasoftware.Opera` |
| Chromium | `chromium` | `org.chromium.Chromium` |

## 📦 Installation

### Prerequisites

- **macOS** (required for ScriptingBridge)
- **Python 3.8+**
- One or more supported Chromium-based browsers installed

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/chromium-bookmark-manager.git
cd chromium-bookmark-manager

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pyobjc-framework-Cocoa pyobjc-framework-ScriptingBridge
```

## 🚀 Usage

### Basic Commands

```bash
# Activate virtual environment (required before running)
source .venv/bin/activate

# List all bookmarks (default: Chrome)
python chromium_bookmark_manager.py list

# Use a different browser
python chromium_bookmark_manager.py -b brave list
python chromium_bookmark_manager.py -b edge list

# Show supported browsers
python chromium_bookmark_manager.py browsers
```

### Command Reference

| Action | Command | Description |
|--------|---------|-------------|
| **List** | `python chromium_bookmark_manager.py list [--depth N]` | Display all bookmarks |
| **Search** | `python chromium_bookmark_manager.py search "term"` | Search in bookmarks |
| **Add** | `python chromium_bookmark_manager.py add "Title" "URL" [--folder "Path"]` | Add a bookmark |
| **Create Folder** | `python chromium_bookmark_manager.py create_folder "Path/To/Folder"` | Create a folder |
| **Delete** | `python chromium_bookmark_manager.py delete "Name"` | Delete an item |
| **Browsers** | `python chromium_bookmark_manager.py browsers` | List supported browsers |

### Examples

```bash
# List bookmarks in Brave with max depth of 2
python chromium_bookmark_manager.py -b brave list --depth 2

# Search for "github" in Edge
python chromium_bookmark_manager.py -b edge search "github"

# Add a bookmark to Chrome
python chromium_bookmark_manager.py add "GitHub" "https://github.com"

# Add bookmark to a specific folder in Brave
python chromium_bookmark_manager.py -b brave add "Docs" "https://docs.python.org" --folder "Bookmarks Bar/Dev"

# Create a new folder in Arc
python chromium_bookmark_manager.py -b arc create_folder "Bookmarks Bar/Projects/2024"

# Delete a bookmark from Vivaldi
python chromium_bookmark_manager.py -b vivaldi delete "Old Bookmark"
```

## 🔧 How It Works

This tool uses **ScriptingBridge** (macOS's AppleScript bridge for Python) to communicate directly with Chromium-based browsers. Since all Chromium browsers share a similar scripting dictionary, the same commands work across all supported browsers.

### Why ScriptingBridge?

- ⚡ **Instant updates** — no need to reload the browser
- 🔒 **Safe** — uses the browser's official scripting API
- 🔄 **Real-time** — changes are reflected immediately
- 📁 **No file manipulation** — no risk of corrupting bookmark files

## ⚠️ Troubleshooting

### "Browser is not installed or not accessible"

Make sure the browser is:
1. Installed on your system
2. Has been opened at least once
3. Is not blocked by macOS security settings

### Permission Issues

On first run, macOS may ask for permission to control the browser. Go to:
**System Preferences → Security & Privacy → Privacy → Automation**

Grant Python/Terminal access to control your browser.

### Browser Not Listed

If your Chromium-based browser isn't listed, you can find its bundle ID with:

```bash
osascript -e 'id of app "YourBrowserName"'
```

Then modify the `BROWSERS` dictionary in the script.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add support for more browsers
- Improve error handling
- Add new features (export, import, sync, etc.)

## 📄 License

MIT License - feel free to use this in your own projects!

## 🙏 Acknowledgments

- Built with [PyObjC](https://pypi.org/project/pyobjc/)
- Inspired by the need for a fast, CLI-based bookmark manager
