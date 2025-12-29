# 🔖 macOS Chromium Bookmark Manager

A powerful command-line tool for managing bookmarks in **Chromium-based browsers** on **macOS** using ScriptingBridge.

> **Direct manipulation** of bookmarks without import/export — changes appear **instantly** in your browser!

## 🤖 Perfect for AI Assistants

This tool is specifically designed to be used by **AI assistants** (ChatGPT, Claude, Gemini, etc.) to help you organize your bookmarks through natural language commands. The CLI provides:

- ✅ **Clear, parseable output** — Success/error messages for automation
- ✅ **Complete CRUD operations** — Create, Read, Update, Delete
- ✅ **Structured responses** — Easy to process programmatically
- ✅ **Safe operations** — No risk of corrupting bookmark files

### AI Usage Example

Ask your AI assistant:
> "Add a bookmark for GitHub to my Dev folder in Chrome"

The AI can execute:
```bash
python chromium_bookmark_manager.py add "GitHub" "https://github.com" --folder "Bookmarks Bar/Dev"
```

> "Rename my 'Old Project' bookmark to 'Legacy Project'"

```bash
python chromium_bookmark_manager.py rename "Old Project" "Legacy Project"
```

> "Move all my Python bookmarks to a new folder called 'Python Resources'"

```bash
python chromium_bookmark_manager.py create_folder "Bookmarks Bar/Python Resources"
python chromium_bookmark_manager.py move "Python Docs" "Bookmarks Bar/Python Resources"
python chromium_bookmark_manager.py move "PyPI" "Bookmarks Bar/Python Resources"
```

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `list` | 📋 List all bookmarks with tree structure (use `--folders` for folders only) |
| `search` | 🔍 Search bookmarks by title or URL |
| `get` | 📄 Get details of a specific bookmark or folder |
| `add` | ➕ Add a new bookmark |
| `create_folder` | 📁 Create a new folder |
| `rename` | ✏️ Rename a bookmark or folder |
| `set_url` | 🔗 Change the URL of a bookmark |
| `move` | 📦 Move a bookmark to another folder |
| `move_bulk` | 📦 Move multiple bookmarks at once |
| `batch` | 📜 Execute actions from a JSON file |
| `duplicates` | 🔍 Find bookmarks sharing the same URL |
| `sort` | 📏 Sort folder contents alphabetically ⚠️ |
| `delete` | 🗑️ Delete a bookmark or folder ⚠️ |
| `clear` | 🧹 Remove all items from a folder ⚠️ |

> ⚠️ Commands marked with ⚠️ require confirmation (can be skipped with `-y` or `--force`)

---

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

---

## 📦 Installation

### Prerequisites

- **macOS** (required for ScriptingBridge)
- **Python 3.8+**
- One or more supported Chromium-based browsers installed

### Setup

```bash
# Clone the repository
git clone https://github.com/Smax2k/macOS-Chromium-Bookmark-Manager.git
cd macOS-Chromium-Bookmark-Manager

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pyobjc-framework-Cocoa pyobjc-framework-ScriptingBridge
```

---

## 🚀 Usage

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# List all bookmarks (default: Chrome)
python chromium_bookmark_manager.py list

# Use a different browser
python chromium_bookmark_manager.py -b brave list

# Show all supported browsers
python chromium_bookmark_manager.py browsers
```

### Command Reference

#### 📋 List Bookmarks
```bash
# List all bookmarks
python chromium_bookmark_manager.py list

# Limit depth (useful for large bookmark collections)
python chromium_bookmark_manager.py list --depth 2

# List only folders
python chromium_bookmark_manager.py list --folders

# List bookmarks in Brave
python chromium_bookmark_manager.py -b brave list
```

#### 🔍 Search
```bash
# Search by title or URL
python chromium_bookmark_manager.py search "github"

# Limit results
python chromium_bookmark_manager.py search "python" --limit 10
```

#### 📄 Get Details
```bash
# Get info about a bookmark
python chromium_bookmark_manager.py get "GitHub"

# Get info about a folder
python chromium_bookmark_manager.py get "Dev"
```

Output:
```
🔖 Bookmark: GitHub
   URL: https://github.com
   Location: Bookmarks Bar
```

#### ➕ Add Bookmark
```bash
# Add to Bookmarks Bar (default)
python chromium_bookmark_manager.py add "GitHub" "https://github.com"

# Add to a specific folder
python chromium_bookmark_manager.py add "Python Docs" "https://docs.python.org" --folder "Bookmarks Bar/Dev/Python"

# Add to Other Bookmarks
python chromium_bookmark_manager.py add "Archive" "https://example.com" --folder "Other Bookmarks/Old"
```

#### 📁 Create Folder
```bash
# Create in Bookmarks Bar
python chromium_bookmark_manager.py create_folder "Bookmarks Bar/Projects"

# Create nested folders (creates parent folders if needed)
python chromium_bookmark_manager.py create_folder "Bookmarks Bar/Work/2024/Q1"
```

#### ✏️ Rename
```bash
# Rename a bookmark
python chromium_bookmark_manager.py rename "Old Name" "New Name"

# Rename a folder
python chromium_bookmark_manager.py rename "Dev" "Development"
```

#### 🔗 Change URL
```bash
# Update the URL of an existing bookmark
python chromium_bookmark_manager.py set_url "GitHub" "https://github.com/dashboard"
```

#### 📦 Move Bookmark
```bash
# Move a bookmark to another folder
python chromium_bookmark_manager.py move "GitHub" "Bookmarks Bar/Dev"

# Move to Other Bookmarks
python chromium_bookmark_manager.py move "Old Site" "Other Bookmarks/Archive"
```

#### 📜 Batch Execution (Recipes)
Execute a list of actions defined in a JSON file.

```bash
# Apply a recipe
python chromium_bookmark_manager.py batch recipe_example.json

# Skip confirmation
python chromium_bookmark_manager.py batch recipe_example.json --force
```

**JSON Format Example (`recipe_example.json`):**

```json
{
  "comment": "Monthly cleanup",
  "actions": [
    {
      "action": "create_folder",
      "path": "Bookmarks Bar/New Projects"
    },
    {
      "action": "move_bulk",
      "destination": "Bookmarks Bar/New Projects",
      "items": ["Project A", "Project B"]
    },
    {
      "action": "delete",
      "name": "Bookmarks Bar/Temp"
    }
  ]
}
```

**Supported Actions:** `create_folder`, `add`, `move`, `move_bulk`, `rename`, `set_url`, `delete`, `clear`, `sort`.

#### 🗑️ Delete
```bash
# Delete a bookmark (will ask for confirmation)
python chromium_bookmark_manager.py delete "Old Bookmark"

# Delete without confirmation (for scripts/AI)
python chromium_bookmark_manager.py delete "Old Bookmark" -y

# Delete a folder (and all its contents)
python3 chromium_bookmark_manager.py delete "Temp Folder" --force
```

#### 🧹 Clear Folder
```bash
# Remove all items from a folder (requires confirmation)
python3 chromium_bookmark_manager.py clear "Bookmarks Bar/Temp"

# Clear without confirmation
python3 chromium_bookmark_manager.py clear "Bookmarks Bar/Temp" -y
```

#### 📏 Sort Alphabetically
```bash
# Sort a folder (requires confirmation)
python chromium_bookmark_manager.py sort "Bookmarks Bar/Archives"

# Sort without confirmation
python chromium_bookmark_manager.py sort "Bookmarks Bar/Archives" --force
```

#### 🔍 Find Duplicates
```bash
# List all bookmarks sharing the same URL
python chromium_bookmark_manager.py duplicates
```

#### 📦 Bulk Move
```bash
# Move multiple bookmarks to a folder
python chromium_bookmark_manager.py move_bulk "Bookmarks Bar/Projects" "Project A" "Project B" "Link C"
```

---

## ⚡ Direct Browser Interaction

Unlike other tools that manipulate backup files, this tool communicates **directly** with your browser instance via ScriptingBridge.

> [!IMPORTANT]
> **No intermediate files needed!** Don't waste time exporting your bookmarks to `.txt` or `.html` for analysis. Query the script directly — data is always up-to-date and changes are instant.

---

## 🛡️ Safety Features

This tool modifies your bookmarks **directly and permanently**. To protect your data:

### ⚠️ Warning Before Modifications

When running any command that modifies bookmarks (`add`, `delete`, `rename`, etc.), you'll see:

```
============================================================
⚠️  WARNING - DIRECT BOOKMARK MODIFICATION
============================================================
You are about to modify bookmarks in Google Chrome.
Changes are IMMEDIATE and PERMANENT.

💡 RECOMMENDATION: Export your bookmarks before continuing!
   In Google Chrome: Menu > Bookmarks > Bookmark Manager
   Then: ⋮ > Export bookmarks
============================================================
```

### 🔐 Confirmation for Dangerous Commands

`delete`, `clear`, and `sort` require confirmation:

```
⚠️  Do you really want to delete 'My Bookmark'? [y/N]: 
```

To skip confirmation (for automation/AI):
```bash
python chromium_bookmark_manager.py delete "Bookmark" -y
python chromium_bookmark_manager.py clear "Folder" --force
```

### 💾 Recommended Workflow

1. **Export your bookmarks** before making changes
2. Use `list` or `search` to verify items exist
3. Run the modifying command
4. Verify changes in your browser

---

## 🔧 How It Works

This tool uses **ScriptingBridge** (macOS's AppleScript bridge for Python) to communicate directly with Chromium-based browsers. Since all Chromium browsers share a similar scripting dictionary, the same commands work across all supported browsers.

### Architecture

```
┌─────────────────────┐
│   Your Terminal     │
│   or AI Assistant   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  chromium_bookmark  │
│     _manager.py     │
└──────────┬──────────┘
           │ ScriptingBridge
           ▼
┌─────────────────────┐
│  Chrome / Brave /   │
│  Edge / Arc / ...   │
└─────────────────────┘
```

### Why ScriptingBridge?

| Approach | Pros | Cons |
|----------|------|------|
| **ScriptingBridge** ✅ | Instant updates, safe, real-time | macOS only |
| File manipulation | Cross-platform | Risk of corruption, requires browser restart |
| Browser extension | Cross-platform | Complex setup, security concerns |

---

## ⚠️ Troubleshooting

### "Browser is not installed or not accessible"

Make sure the browser is:
1. ✅ Installed on your system
2. ✅ Has been opened at least once
3. ✅ Is allowed in macOS security settings

### Permission Issues

On first run, macOS may ask for permission. Go to:

**System Preferences → Security & Privacy → Privacy → Automation**

Grant Python/Terminal access to control your browser.

### Browser Not Listed

Find your browser's bundle ID:
```bash
osascript -e 'id of app "YourBrowserName"'
```

Then add it to the `BROWSERS` dictionary in the script.

---

## 🐍 Python API

You can also use this as a Python library:

```python
from chromium_bookmark_manager import BookmarkManager

# Connect to Chrome (default)
manager = BookmarkManager()

# Or connect to another browser
manager = BookmarkManager("brave")

# List bookmarks (folders only)
manager.list_all(max_depth=2, folders_only=True)

# Search
results = manager.search("github")

# Add bookmark
manager.add_bookmark("GitHub", "https://github.com", "Bookmarks Bar/Dev")

# Rename
manager.rename_item("Old Name", "New Name")

# Change URL
manager.set_url("GitHub", "https://github.com/new")

# Move
manager.move_item("GitHub", "Bookmarks Bar/Archive")

# Get details
info = manager.get_item("GitHub")
print(info)  # {'type': 'bookmark', 'title': 'GitHub', 'url': '...', 'location': '...'}

# Delete
manager.delete_item("Old Bookmark")

# Clear folder
manager.clear_folder("Bookmarks Bar/Temp")

# Sort folder alphabetically
manager.sort_folder("Bookmarks Bar/Dev")

# Find duplicate bookmarks (same URL)
duplicates = manager.find_duplicates()

# Bulk move bookmarks
manager.move_bulk("Bookmarks Bar/Archive", ["Bookmark1", "Bookmark2", "Bookmark3"])
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🌐 Add support for more browsers
- 🐛 Improve error handling
- ✨ Add new features (export, import, sync, etc.)
- 📚 Improve documentation

---

## 📄 License

MIT License - feel free to use this in your own projects!

---

## 🙏 Acknowledgments

- **Inspired by [Rob Perc's ChromeBookmarkEditor](https://github.com/robperc/ChromeBookmarkEditor)** - The original Python ScriptingBridge implementation for Chrome bookmarks
- Built with [PyObjC](https://pypi.org/project/pyobjc/)
- Designed for seamless AI assistant integration
