#!/usr/bin/env python3
"""
macOS Chromium Bookmark Manager - Manage bookmarks for Chromium-based browsers via ScriptingBridge
Direct bookmark manipulation in Chromium browsers (macOS only)

Supported browsers: Chrome, Brave, Edge, Arc, Vivaldi, Comet, Opera, Chromium
"""

# Hide python rocket ship from popping up in Dock when run.
import AppKit
info = AppKit.NSBundle.mainBundle().infoDictionary()
info['CFBundleIconFile'] = u'PythonApplet.icns'
info['LSUIElement'] = True

from ScriptingBridge import SBApplication
import sys
import argparse
import time
import html
import re
import json
import os

# Supported Chromium-based browsers and their bundle identifiers
BROWSERS = {
    "chrome": {
        "bundle_id": "com.google.Chrome",
        "name": "Google Chrome",
    },
    "brave": {
        "bundle_id": "com.brave.Browser",
        "name": "Brave Browser",
    },
    "edge": {
        "bundle_id": "com.microsoft.edgemac",
        "name": "Microsoft Edge",
    },
    "arc": {
        "bundle_id": "company.thebrowser.Browser",
        "name": "Arc Browser",
    },
    "vivaldi": {
        "bundle_id": "com.vivaldi.Vivaldi",
        "name": "Vivaldi",
    },
    "comet": {
        "bundle_id": "ai.perplexity.comet",
        "name": "Comet (Perplexity)",
    },
    "opera": {
        "bundle_id": "com.operasoftware.Opera",
        "name": "Opera",
    },
    "chromium": {
        "bundle_id": "org.chromium.Chromium",
        "name": "Chromium",
    },
}

DEFAULT_BROWSER = "chrome"


class BrowserApp:
    """Base class for browser application connection via ScriptingBridge."""
    
    def __init__(self, browser_key=DEFAULT_BROWSER):
        if browser_key not in BROWSERS:
            available = ", ".join(BROWSERS.keys())
            raise ValueError(f"Unknown browser: '{browser_key}'. Available: {available}")
        
        browser_info = BROWSERS[browser_key]
        self.browser_name = browser_info["name"]
        self.bundle_id = browser_info["bundle_id"]
        
        self.app = SBApplication.applicationWithBundleIdentifier_(self.bundle_id)
        if not self.app:
            raise RuntimeError(
                f"{self.browser_name} is not installed or not accessible.\n"
                f"Bundle ID: {self.bundle_id}"
            )


class BookmarkManager(BrowserApp):
    """Main bookmark manager for Chromium-based browsers."""
    
    def __init__(self, browser_key=DEFAULT_BROWSER):
        super().__init__(browser_key)
        self.bookmarks_bar = Folder(self.app.bookmarksBar(), self.app)
        self.other_bookmarks = Folder(self.app.otherBookmarks(), self.app)
        self._index = None  # Cache local pour la session
    
    def index_bookmarks(self):
        """Index all bookmarks in memory for fast lookup."""
        print("🔍 Indexing bookmarks for faster processing...")
        start_time = time.time()
        self._index = {"bookmarks": {}, "folders": {}}
        
        def collect(folder, path):
            # Index current folder
            f_title = self._normalize(folder.title())
            if f_title not in self._index["folders"]:
                self._index["folders"][f_title] = []
            self._index["folders"][f_title].append((folder, path))
            
            # Index bookmarks in this folder
            for b in folder.bookmarks:
                b_title = self._normalize(b.title())
                if b_title not in self._index["bookmarks"]:
                    self._index["bookmarks"][b_title] = []
                self._index["bookmarks"][b_title].append((b, path))
            
            # Recurse into subfolders
            for f in folder.folders:
                collect(Folder(f, self.app), f"{path}/{str(f.title())}")
        
        collect(self.bookmarks_bar, "Bookmarks Bar")
        collect(self.other_bookmarks, "Other Bookmarks")
        
        duration = time.time() - start_time
        count = sum(len(v) for v in self._index["bookmarks"].values())
        print(f"✨ Indexed {count} bookmarks in {duration:.2f}s")
    
    def list_all(self, folder_path=None, max_depth=None, folders_only=False):
        """Display bookmarks."""
        if folder_path:
            target = self._resolve_path(folder_path)
            if not target:
                print(f"❌ Folder '{folder_path}' not found")
                return
            print(f"📂 {folder_path}")
            target.list_tree(indent=1, max_depth=max_depth, folders_only=folders_only)
        else:
            print(f"📂 Bookmarks Bar")
            self.bookmarks_bar.list_tree(indent=1, max_depth=max_depth, folders_only=folders_only)
            print(f"\n📂 Other Bookmarks")
            self.other_bookmarks.list_tree(indent=1, max_depth=max_depth, folders_only=folders_only)
    
    def search(self, query, limit=50):
        """Search in all bookmarks."""
        results = []
        results.extend(self.bookmarks_bar.search(query, "Bookmarks Bar"))
        results.extend(self.other_bookmarks.search(query, "Other Bookmarks"))
        return results[:limit]
    
    def add_bookmark(self, title, url, folder_path=None):
        """Add a bookmark. folder_path: 'Bookmarks Bar/Folder' or 'Other Bookmarks/Folder'"""
        if folder_path:
            parts = folder_path.split('/')
            root_lower = parts[0].lower()
            
            if root_lower in ['bookmarks bar', 'barre de favoris']:
                target = self.bookmarks_bar
                parts = parts[1:]
            elif root_lower in ['other bookmarks', 'autres favoris']:
                target = self.other_bookmarks
                parts = parts[1:]
            else:
                target = self.bookmarks_bar
            
            for part in parts:
                if part:
                    folder = target.get_folder(part)
                    if folder:
                        target = folder
                    else:
                        print(f"Folder '{part}' not found, creating...")
                        target.add_folder(part)
                        target = target.get_folder(part)
        else:
            target = self.bookmarks_bar
        
        target.add_bookmark(title, url)
        print(f"✅ Bookmark '{title}' added")
    
    def create_folder(self, folder_path):
        """Create a folder. folder_path: 'Bookmarks Bar/New/Folder'"""
        parts = folder_path.split('/')
        root_lower = parts[0].lower()
        
        if root_lower in ['bookmarks bar', 'barre de favoris']:
            target = self.bookmarks_bar
            parts = parts[1:]
        elif root_lower in ['other bookmarks', 'autres favoris']:
            target = self.other_bookmarks
            parts = parts[1:]
        else:
            target = self.bookmarks_bar
        
        for part in parts:
            if part:
                folder = target.get_folder(part)
                if folder:
                    target = folder
                else:
                    target.add_folder(part)
                    target = target.get_folder(part)
                    print(f"✅ Folder '{part}' created")
    
    def _resolve_path(self, folder_path):
        """Resolve a folder path to a Folder object."""
        if not folder_path:
            return self.bookmarks_bar
        
        parts = folder_path.split('/')
        root_lower = parts[0].lower()
        
        if root_lower in ['bookmarks bar', 'barre de favoris']:
            target = self.bookmarks_bar
            parts = parts[1:]
        elif root_lower in ['other bookmarks', 'autres favoris']:
            target = self.other_bookmarks
            parts = parts[1:]
        else:
            target = self.bookmarks_bar
        
        for part in parts:
            if part:
                folder = target.get_folder(part)
                if folder:
                    target = folder
                else:
                    return None
        
        return target
    
    def _normalize(self, text):
        """Normalize whitespace, decode HTML entities, and remove hidden characters."""
        if not text:
            return ""
        # Decode entities
        temp = html.unescape(str(text))
        # Remove zero-width characters and control chars (like \u200e)
        temp = re.sub(r'[\u200b-\u200f\uFEFF\u202a-\u202e]', '', temp)
        # Normalize whitespace
        return " ".join(temp.split())

    def _find_item(self, name, item_type="both"):
        """Find a bookmark or folder by name. Uses index if available."""
        target_name = self._normalize(name)
        
        # Use index if available (MUCH faster)
        if self._index:
            results = []
            if item_type in ["both", "bookmark"] and target_name in self._index["bookmarks"]:
                for item, loc in self._index["bookmarks"][target_name]:
                    results.append((item, loc, "bookmark"))
            if item_type in ["both", "folder"] and target_name in self._index["folders"]:
                for item, loc in self._index["folders"][target_name]:
                    # The root folders (Bookmarks Bar/Other Bookmarks) don't have titles in the same way
                    # but they are in the folders index if collected.
                    results.append((item, loc, "folder"))
            
            if results:
                # Prioritize shorter paths (closer to root)
                results.sort(key=lambda x: len(x[1].split('/')))
                return results[0]
            return (None, None, None)

        # Fallback to recursive scan if no index
        def search_recursive(folder, folder_name):
            # Check bookmarks in this folder
            if item_type in ["both", "bookmark"]:
                for b in folder.bookmarks:
                    if self._normalize(b.title()) == target_name:
                        return (b, folder_name, "bookmark")
            
            # Check subfolders
            for f in folder.folders:
                f_title_raw = str(f.title())
                f_title = self._normalize(f_title_raw)
                
                if item_type in ["both", "folder"] and f_title == target_name:
                    return (Folder(f, self.app), folder_name, "folder")
                
                res = search_recursive(Folder(f, self.app), f"{folder_name}/{f_title_raw}")
                if res[0]:
                    return res
            
            return (None, None, None)

        res = search_recursive(self.bookmarks_bar, "Bookmarks Bar")
        if res[0]: return res
        
        res = search_recursive(self.other_bookmarks, "Other Bookmarks")
        return res
    
    def delete_item(self, name):
        """Delete a bookmark or folder by name."""
        item, location, item_type = self._find_item(name)
        
        if item:
            if item_type == "folder":
                item.delete()
            else:
                item.delete()
            print(f"✅ {item_type.capitalize()} '{name}' deleted from {location}")
            return True
        
        print(f"❌ '{name}' not found")
        return False
    
    def rename_item(self, name, new_name):
        """Rename a bookmark or folder."""
        item, location, item_type = self._find_item(name)
        
        if item:
            if item_type == "folder":
                item.root.setTitle_(new_name)
            else:
                item.setTitle_(new_name)
            print(f"✅ {item_type.capitalize()} '{name}' renamed to '{new_name}'")
            return True
        
        print(f"❌ '{name}' not found")
        return False
    
    def set_url(self, name, new_url):
        """Change the URL of a bookmark."""
        item, location, item_type = self._find_item(name, "bookmark")
        
        if item:
            item.setURL_(new_url)
            print(f"✅ Bookmark '{name}' URL updated to '{new_url}'")
            return True
        
        print(f"❌ Bookmark '{name}' not found")
        return False
    
    def get_item(self, name):
        """Get details of a bookmark or folder."""
        item, location, item_type = self._find_item(name)
        
        if item:
            if item_type == "folder":
                folder_obj = item
                bookmark_count = len(list(folder_obj.bookmarks))
                subfolder_count = len(list(folder_obj.folders))
                print(f"📁 Folder: {folder_obj.title()}")
                print(f"   Location: {location}")
                print(f"   Bookmarks: {bookmark_count}")
                print(f"   Subfolders: {subfolder_count}")
                return {
                    "type": "folder",
                    "title": folder_obj.title(),
                    "location": location,
                    "bookmarks": bookmark_count,
                    "subfolders": subfolder_count
                }
            else:
                title = str(item.title())
                url = str(item.URL())
                print(f"🔖 Bookmark: {title}")
                print(f"   URL: {url}")
                print(f"   Location: {location}")
                return {
                    "type": "bookmark",
                    "title": title,
                    "url": url,
                    "location": location
                }
        
        print(f"❌ '{name}' not found")
        return None
    
    def clear_folder(self, folder_path):
        """Remove all items from a folder."""
        target = self._resolve_path(folder_path)
        
        if not target:
            print(f"❌ Folder '{folder_path}' not found")
            return False
        
        count = len(list(target.folders)) + len(list(target.bookmarks))
        target.remove_all()
        print(f"✅ Cleared {count} items from '{folder_path}'")
        return True
    
    def move_item(self, name, destination_path):
        """Move a bookmark to another folder safely."""
        item, location, item_type = self._find_item(name, "bookmark")
        
        if not item:
            print(f"❌ Bookmark '{name}' not found")
            return False
        
        destination = self._resolve_path(destination_path)
        if not destination:
            print(f"❌ Destination folder '{destination_path}' not found")
            return False
        
        # Check if already in destination (normalize paths to compare)
        # location example: "Bookmarks Bar/Folder"
        # destination_path example: "Bookmarks Bar/Folder/"
        current_loc_norm = self._normalize(location).lower().strip('/')
        dest_loc_norm = self._normalize(destination_path).lower().strip('/')
        
        if current_loc_norm == dest_loc_norm:
            print(f"ℹ️  Bookmark '{name}' is already in '{location}' - Skipped")
            return True
        
        # Get bookmark info
        title = str(item.title())
        url = str(item.URL())
        
        # Step 1: Add to destination FIRST (safe)
        destination.add_bookmark(title, url)
        
        # Step 2: Delete from original
        item.delete()
        
        # Update index if it exists
        if self._index and name in self._index["bookmarks"]:
            pass
            
        print(f"✅ Bookmark '{name}' moved to '{destination_path}'")
        return True
    
    def find_duplicates(self):
        """Find bookmarks with the same URL."""
        all_bookmarks = []
        
        def collect(folder, path):
            for b in folder.bookmarks:
                all_bookmarks.append({
                    "title": str(b.title()),
                    "url": str(b.URL()),
                    "path": path
                })
            for f in folder.folders:
                collect(Folder(f, self.app), f"{path}/{f.title()}")
        
        collect(self.bookmarks_bar, "Bookmarks Bar")
        collect(self.other_bookmarks, "Other Bookmarks")
        
        url_map = {}
        for b in all_bookmarks:
            url = b["url"]
            if url not in url_map:
                url_map[url] = []
            url_map[url].append(b)
        
        duplicates = {url: items for url, items in url_map.items() if len(items) > 1}
        
        if not duplicates:
            print("✨ No duplicates found!")
            return
        
        print(f"🔍 Found {len(duplicates)} URLs with duplicates:\n")
        for url, items in duplicates.items():
            print(f"🔗 URL: {url}")
            for item in items:
                print(f"   - {item['title']} [In: {item['path']}]")
            print()

    def move_bulk(self, names, destination_path):
        """Move multiple bookmarks efficiently using index."""
        # Index everything once
        if not self._index:
            self.index_bookmarks()
            
        destination = self._resolve_path(destination_path)
        if not destination:
            print(f"❌ Destination folder '{destination_path}' not found")
            return False
        
        success_count = 0
        for name in names:
            item, location, item_type = self._find_item(name, "bookmark")
            if item:
                title = str(item.title())
                url = str(item.URL())
                # Add then delete
                destination.add_bookmark(title, url)
                item.delete()
                print(f"  ✅ Moved '{html.unescape(title)}'")
                success_count += 1
            else:
                print(f"  ⚠️ Bookmark '{name}' not found")
        
        # Reset index as structure has changed
        self._index = None
        
        print(f"\n📦 Successfully moved {success_count}/{len(names)} items to '{destination_path}'")
        return True

    
    def process_batch_file(self, file_path, force=False):
        """Execute a list of actions defined in a JSON file."""
        if not os.path.exists(file_path):
            print(f"❌ File '{file_path}' not found")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON file: {e}")
            return
            
        actions = plan.get('actions', [])
        if not actions:
            print("⚠️  No actions found in the plan.")
            return
            
        print(f"📋 Batch Plan found: {len(actions)} actions")
        if 'comment' in plan:
            print(f"ℹ️  Comment: {plan['comment']}")
        
        # Summary of actions
        summary = {}
        for act in actions:
            atype = act.get('action', 'unknown')
            summary[atype] = summary.get(atype, 0) + 1
            
        print("\nSummary of operations:")
        for atype, count in summary.items():
            print(f"  - {atype}: {count}")
            
        if not force and not confirm_action("Execute this plan?"):
            return

        print("\n🚀 Executing plan...")
        
        # Mapping action names to methods
        # Lambda wrappers to map JSON args to method args
        action_map = {
            "create_folder": lambda m, a: m.create_folder(a.get('path')),
            "add": lambda m, a: m.add_bookmark(a.get('title'), a.get('url'), a.get('folder')),
            "move": lambda m, a: m.move_item(a.get('name'), a.get('destination')),
            "move_bulk": lambda m, a: m.move_bulk(a.get('items'), a.get('destination')),
            "rename": lambda m, a: m.rename_item(a.get('name'), a.get('new_name')),
            "set_url": lambda m, a: m.set_url(a.get('name'), a.get('new_url')),
            "delete": lambda m, a: m.delete_item(a.get('name')),
            "clear": lambda m, a: m.clear_folder(a.get('folder')),
            "sort": lambda m, a: m.sort_folder(a.get('folder'))
        }

        success_count = 0
        for i, action_data in enumerate(actions, 1):
            action_type = action_data.get('action')
            if action_type not in action_map:
                print(f"⚠️  Action {i}: Unknown action type '{action_type}' - Skipped")
                continue
                
            print(f"\n[Action {i}/{len(actions)}] {action_type.upper()}")
            try:
                # Execute the action
                # We check for specific 'force' flags in args if needed, but usually batch implies force for confirmations
                # For safety, destructive single actions in batch still use the manager's methods which print logs.
                # However, confirm_action inside methods (like delete) might block.
                # We need to consider if we want to bypass individual confirmations in batch mode.
                # Since we confirmed the WHOLE plan at start, we should probably simulate force=True for individual actions?
                # But our methods don't all take force param. 'delete' and 'clear' do via CLI args but methods like delete_item don't ask, they just do.
                # The CLI wrapper asks. The methods in BookmarkManager class DO NOT ask confirmation (except implicitly via being called).
                # Wait, confirm_action is in main(), logic is: if confirm... manager.delete_item(). 
                # So manager methods are already direct. Safe.
                
                action_map[action_type](self, action_data)
                success_count += 1
            except Exception as e:
                print(f"❌ Error executing action {i}: {e}")
                if not confirm_action("Continue to next action?", default=True):
                    print("🛑 Execution stopped by user.")
                    break
        
        print(f"\n✨ Batch processing completed. {success_count}/{len(actions)} actions successful.")

    def sort_folder(self, folder_path):
        """Sort items in a folder alphabetically."""
        target = self._resolve_path(folder_path)
        if not target:
            print(f"❌ Folder '{folder_path}' not found")
            return False
        
        # Get all items
        items = []
        for b in target.bookmarks:
            items.append({"type": "bookmark", "title": str(b.title()), "url": str(b.URL())})
        for f in target.folders:
            items.append({"type": "folder", "title": str(f.title())})
            
        if not items:
            print(f"ℹ️ Folder '{folder_path}' is empty.")
            return True
        
        # Sort items (case-insensitive)
        items.sort(key=lambda x: x["title"].lower())
        
        # Clear items
        target.remove_all()
        # Small delay to ensure deletion is processed by the browser
        time.sleep(0.5)
        
        # Re-add in order
        for item in items:
            if item["type"] == "bookmark":
                target.add_bookmark(item["title"], item["url"])
            else:
                target.add_folder(item["title"])
        
        print(f"✅ Sorted {len(items)} items in '{folder_path}'")
        return True


class Folder(BrowserApp):
    """Represents a bookmark folder."""
    
    def __init__(self, root, app=None):
        if app:
            self.app = app
        else:
            super().__init__()
        self.root = root
        self.folders = self.root.bookmarkFolders()
        self.bookmarks = self.root.bookmarkItems()
    
    def title(self):
        return html.unescape(str(self.root.title()))
    
    def set_title(self, title):
        self.root.setTitle_(title)
    
    def delete(self):
        self.root.delete()
    
    def get_folder(self, title):
        """Find a subfolder by title."""
        for folder in self.folders:
            if str(folder.title()) == title:
                return Folder(folder, self.app)
        return None
    
    def get_bookmark(self, title):
        """Find a bookmark by title."""
        for bookmark in self.bookmarks:
            if str(bookmark.title()) == title:
                return bookmark
        return None
    
    def add_folder(self, title):
        """Create a new subfolder."""
        properties = dict(title=title)
        new_folder = self.app.classForScriptingClass_("bookmark folder").alloc().initWithProperties_(properties)
        self.folders.append(new_folder)
    
    def add_bookmark(self, title, url):
        """Add a new bookmark."""
        properties = dict(title=title, URL=url)
        new_bookmark = self.app.classForScriptingClass_("bookmark item").alloc().initWithProperties_(properties)
        self.bookmarks.append(new_bookmark)
    
    def remove_all(self):
        """Remove all bookmarks and folders."""
        for item in list(self.folders) + list(self.bookmarks):
            item.delete()
    
    def list_tree(self, indent=0, max_depth=None, folders_only=False):
        """Display the tree structure."""
        if max_depth is not None and indent > max_depth:
            return
        
        indent_str = "  " * indent
        
        # Folders
        for folder in self.folders:
            title = html.unescape(str(folder.title()))
            print(f"{indent_str}📁 {title}")
            Folder(folder, self.app).list_tree(indent + 1, max_depth, folders_only)
        
        # Bookmarks
        if not folders_only:
            for bookmark in self.bookmarks:
                title = html.unescape(str(bookmark.title()))
                print(f"{indent_str}🔖 {title} ({bookmark.URL()})")
    
    def search(self, query, parent_path=""):
        """Recursive search."""
        results = []
        query_lower = query.lower()
        
        for bookmark in self.bookmarks:
            title = html.unescape(str(bookmark.title()))
            url = str(bookmark.URL())
            if query_lower in title.lower() or query_lower in url.lower():
                results.append(f"🔖 {title} ({url}) [In: {parent_path}]")
        
        for folder in self.folders:
            folder_title = html.unescape(str(folder.title()))
            if query_lower in folder_title.lower():
                results.append(f"📁 [Folder] {folder_title} [In: {parent_path}]")
            results.extend(Folder(folder, self.app).search(query, f"{parent_path}/{folder_title}"))
        
        return results


def list_browsers():
    """List all supported browsers."""
    print("Supported Chromium-based browsers:\n")
    for key, info in BROWSERS.items():
        print(f"  {key:12} - {info['name']}")
        print(f"               Bundle ID: {info['bundle_id']}")
    print(f"\nDefault browser: {DEFAULT_BROWSER}")


def confirm_action(message, default=False):
    """Ask user for confirmation. Returns True if confirmed."""
    suffix = " [y/N]: " if not default else " [Y/n]: "
    try:
        response = input(f"⚠️  {message}{suffix}").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', 'oui', 'o']
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Operation cancelled.")
        return False


def print_safety_warning(browser_name):
    """Print a safety warning before destructive operations."""
    print("=" * 60)
    print("⚠️  WARNING - DIRECT BOOKMARK MODIFICATION")
    print("=" * 60)
    print(f"You are about to modify bookmarks in {browser_name}.")
    print("Changes are IMMEDIATE and PERMANENT.")
    print("")
    print("💡 RECOMMENDATION: Export your bookmarks before continuing!")
    print(f"   In {browser_name}: Menu > Bookmarks > Bookmark Manager")
    print("   Then: ⋮ > Export bookmarks")
    print("=" * 60)
    print("")


# Commands that modify bookmarks (require a warning)
MODIFYING_COMMANDS = ["add", "create_folder", "rename", "set_url", "move", "delete", "clear", "move_bulk", "sort"]

# Dangerous commands that require confirmation
DANGEROUS_COMMANDS = ["delete", "clear", "sort"]


def main():
    parser = argparse.ArgumentParser(
        description="macOS Chromium Bookmark Manager - Manage bookmarks for Chromium-based browsers via CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                                    # List all bookmarks (default: Chrome)
  %(prog)s list --folders                          # List only folders
  %(prog)s -b brave list --depth 2                 # List Brave bookmarks with max depth 2
  %(prog)s search "github"                         # Search for "github" in bookmarks
  %(prog)s get "GitHub"                            # Get details of a bookmark or folder
  %(prog)s add "GitHub" "https://github.com"       # Add bookmark to Bookmarks Bar
  %(prog)s create_folder "Bookmarks Bar/Projects"  # Create a new folder
  %(prog)s rename "Old Name" "New Name"            # Rename a bookmark or folder
  %(prog)s set_url "GitHub" "https://github.com/new" # Change bookmark URL
  %(prog)s move "GitHub" "Bookmarks Bar/Dev"       # Move bookmark to another folder
  %(prog)s move_bulk "Dest/Folder" "A" "B" "C"     # Move multiple bookmarks at once
  %(prog)s duplicates                              # Find bookmarks with same URL
  %(prog)s sort "Bookmarks Bar/Dev"                # Sort folder alphabetically
  %(prog)s delete "Old Bookmark"                   # Delete (with confirmation)
  %(prog)s delete "Old Bookmark" -y                # Delete without confirmation
  %(prog)s clear "Bookmarks Bar/Temp" --force      # Clear folder without confirmation

Safety:
  - Modifying commands show a warning to export bookmarks first
  - 'delete', 'clear', and 'sort' require confirmation (use -y/--force to skip)
  - Changes are IMMEDIATE and PERMANENT in your browser

AI Usage:
  This tool is designed for AI assistants. Use -y/--force for automation.
        """
    )
    
    parser.add_argument(
        "-b", "--browser",
        choices=list(BROWSERS.keys()),
        default=DEFAULT_BROWSER,
        help=f"Browser to manage (default: {DEFAULT_BROWSER})"
    )
    
    subparsers = parser.add_subparsers(dest="action")
    
    # browsers
    subparsers.add_parser("browsers", help="List supported browsers")
    
    # list
    p_list = subparsers.add_parser("list", help="List bookmarks")
    p_list.add_argument("folder", nargs="?", help="Specific folder to list")
    p_list.add_argument("--depth", type=int, help="Maximum depth to display")
    p_list.add_argument("--folders", action="store_true", help="List only folders")
    
    # search
    p_search = subparsers.add_parser("search", help="Search for bookmarks by title or URL")
    p_search.add_argument("query", help="Search term")
    p_search.add_argument("--limit", type=int, default=50, help="Max number of results")
    
    # get
    p_get = subparsers.add_parser("get", help="Get details of a bookmark or folder")
    p_get.add_argument("name", help="Name of the bookmark or folder")
    
    # add
    p_add = subparsers.add_parser("add", help="Add a new bookmark")
    p_add.add_argument("title", help="Bookmark title")
    p_add.add_argument("url", help="Bookmark URL")
    p_add.add_argument("--folder", help="Target folder path (default: Bookmarks Bar)")
    
    # create_folder
    p_folder = subparsers.add_parser("create_folder", help="Create a new folder")
    p_folder.add_argument("path", help="Folder path (e.g., 'Bookmarks Bar/New Folder')")
    
    # rename
    p_rename = subparsers.add_parser("rename", help="Rename a bookmark or folder")
    p_rename.add_argument("name", help="Current name of the item")
    p_rename.add_argument("new_name", help="New name for the item")
    
    # set_url
    p_seturl = subparsers.add_parser("set_url", help="Change the URL of a bookmark")
    p_seturl.add_argument("name", help="Name of the bookmark")
    p_seturl.add_argument("new_url", help="New URL")
    
    # move
    p_move = subparsers.add_parser("move", help="Move a bookmark to another folder")
    p_move.add_argument("name", help="Name of the bookmark to move")
    p_move.add_argument("destination", help="Destination folder path")
    
    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a bookmark or folder (requires confirmation)")
    p_delete.add_argument("name", help="Name of the item to delete")
    p_delete.add_argument("-y", "--force", action="store_true", help="Skip confirmation prompt")
    
    # clear
    p_clear = subparsers.add_parser("clear", help="Remove all items from a folder (requires confirmation)")
    p_clear.add_argument("folder", help="Folder path to clear")
    p_clear.add_argument("-y", "--force", action="store_true", help="Skip confirmation prompt")
    
    # duplicates
    subparsers.add_parser("duplicates", help="Find duplicate bookmarks (same URL)")
    
    # move_bulk
    p_movebulk = subparsers.add_parser("move_bulk", help="Move multiple bookmarks to a folder")
    p_movebulk.add_argument("destination", help="Destination folder path")
    p_movebulk.add_argument("names", nargs="+", help="Names of bookmarks to move")
    
    # sort
    p_sort = subparsers.add_parser("sort", help="Sort elements in a folder alphabetically")
    p_sort.add_argument("folder", help="Folder path to sort")
    p_sort.add_argument("-y", "--force", action="store_true", help="Skip confirmation prompt")
    
    # batch
    p_batch = subparsers.add_parser("batch", help="Execute actions from a JSON file")
    p_batch.add_argument("file", help="Path to the JSON plan file")
    p_batch.add_argument("-y", "--force", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(0)
    
    if args.action == "browsers":
        list_browsers()
        sys.exit(0)
    
    try:
        manager = BookmarkManager(args.browser)
        print(f"🌐 Connected to {manager.browser_name}\n")
        
        # Show warning for commands that modify bookmarks
        if args.action in MODIFYING_COMMANDS:
            print_safety_warning(manager.browser_name)
        
        if args.action == "list":
            manager.list_all(folder_path=args.folder, max_depth=args.depth, folders_only=args.folders)
        elif args.action == "search":
            results = manager.search(args.query, args.limit)
            if not results:
                print("No results found.")
            for r in results:
                print(r)
        elif args.action == "get":
            manager.get_item(args.name)
        elif args.action == "add":
            manager.add_bookmark(args.title, args.url, args.folder)
        elif args.action == "create_folder":
            manager.create_folder(args.path)
        elif args.action == "rename":
            manager.rename_item(args.name, args.new_name)
        elif args.action == "set_url":
            manager.set_url(args.name, args.new_url)
        elif args.action == "move":
            manager.move_item(args.name, args.destination)
        elif args.action == "delete":
            # Confirmation required for delete
            if args.force or confirm_action(f"Do you really want to delete '{args.name}'?"):
                manager.delete_item(args.name)
        elif args.action == "clear":
            # Confirmation required for clear
            if args.force or confirm_action(f"Do you really want to CLEAR all items in '{args.folder}'?"):
                manager.clear_folder(args.folder)
            else:
                print("❌ Operation cancelled.")
        elif args.action == "batch":
            manager.process_batch_file(args.file, args.force)
        elif args.action == "duplicates":
            manager.find_duplicates()
        elif args.action == "move_bulk":
            manager.move_bulk(args.names, args.destination)
        elif args.action == "sort":
            # Sorting is considered dangerous as it recreates items (clear + add)
            if args.force or confirm_action(f"Do you really want to SORT folder '{args.folder}'?"):
                manager.sort_folder(args.folder)
            else:
                print("❌ Operation cancelled.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
