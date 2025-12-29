#!/usr/bin/env python3
"""
Chromium Bookmark Manager - Manage bookmarks for Chromium-based browsers via ScriptingBridge
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
    
    def list_all(self, max_depth=None):
        """Display all bookmarks."""
        print(f"📂 Bookmarks Bar")
        self.bookmarks_bar.list_tree(indent=1, max_depth=max_depth)
        print(f"\n📂 Other Bookmarks")
        self.other_bookmarks.list_tree(indent=1, max_depth=max_depth)
    
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
    
    def _find_item(self, name, item_type="both"):
        """Find a bookmark or folder by name. Returns (item, location, type)."""
        # Search in bookmarks bar
        if item_type in ["both", "bookmark"]:
            item = self.bookmarks_bar.get_bookmark(name)
            if item:
                return (item, "Bookmarks Bar", "bookmark")
        
        if item_type in ["both", "folder"]:
            folder = self.bookmarks_bar.get_folder(name)
            if folder:
                return (folder, "Bookmarks Bar", "folder")
        
        # Search in other bookmarks
        if item_type in ["both", "bookmark"]:
            item = self.other_bookmarks.get_bookmark(name)
            if item:
                return (item, "Other Bookmarks", "bookmark")
        
        if item_type in ["both", "folder"]:
            folder = self.other_bookmarks.get_folder(name)
            if folder:
                return (folder, "Other Bookmarks", "folder")
        
        return (None, None, None)
    
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
        """Move a bookmark to another folder."""
        item, location, item_type = self._find_item(name, "bookmark")
        
        if not item:
            print(f"❌ Bookmark '{name}' not found")
            return False
        
        destination = self._resolve_path(destination_path)
        if not destination:
            print(f"❌ Destination folder '{destination_path}' not found")
            return False
        
        # Get bookmark info before deletion
        title = str(item.title())
        url = str(item.URL())
        
        # Delete from original location and add to new one
        item.delete()
        destination.add_bookmark(title, url)
        
        print(f"✅ Bookmark '{name}' moved to '{destination_path}'")
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
        return str(self.root.title())
    
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
    
    def list_tree(self, indent=0, max_depth=None):
        """Display the tree structure."""
        if max_depth is not None and indent > max_depth:
            return
        
        indent_str = "  " * indent
        
        # Folders
        for folder in self.folders:
            print(f"{indent_str}📁 {folder.title()}")
            Folder(folder, self.app).list_tree(indent + 1, max_depth)
        
        # Bookmarks
        for bookmark in self.bookmarks:
            print(f"{indent_str}🔖 {bookmark.title()} ({bookmark.URL()})")
    
    def search(self, query, parent_path=""):
        """Recursive search."""
        results = []
        query_lower = query.lower()
        
        for bookmark in self.bookmarks:
            title = str(bookmark.title())
            url = str(bookmark.URL())
            if query_lower in title.lower() or query_lower in url.lower():
                results.append(f"🔖 {title} ({url}) [In: {parent_path}]")
        
        for folder in self.folders:
            folder_title = str(folder.title())
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
    print("⚠️  ATTENTION - MODIFICATION DIRECTE DES FAVORIS")
    print("=" * 60)
    print(f"Vous allez modifier les favoris de {browser_name}.")
    print("Les changements sont IMMÉDIATS et PERMANENTS.")
    print("")
    print("💡 RECOMMANDATION: Exportez vos favoris avant de continuer !")
    print(f"   Dans {browser_name}: Menu > Favoris > Gestionnaire de favoris")
    print("   Puis: ⋮ > Exporter les favoris")
    print("=" * 60)
    print("")


# Commandes qui modifient les favoris (nécessitent un avertissement)
MODIFYING_COMMANDS = ["add", "create_folder", "rename", "set_url", "move", "delete", "clear"]

# Commandes dangereuses qui nécessitent une confirmation
DANGEROUS_COMMANDS = ["delete", "clear"]


def main():
    parser = argparse.ArgumentParser(
        description="Chromium Bookmark Manager - Manage bookmarks for Chromium-based browsers via CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                                    # List all bookmarks (default: Chrome)
  %(prog)s -b brave list --depth 2                 # List Brave bookmarks with max depth 2
  %(prog)s search "github"                         # Search for "github" in bookmarks
  %(prog)s add "GitHub" "https://github.com"       # Add bookmark to Bookmarks Bar
  %(prog)s create_folder "Bookmarks Bar/Projects"  # Create a new folder
  %(prog)s rename "Old Name" "New Name"            # Rename a bookmark or folder
  %(prog)s delete "Old Bookmark"                   # Delete (with confirmation)
  %(prog)s delete "Old Bookmark" -y                # Delete without confirmation
  %(prog)s clear "Bookmarks Bar/Temp" --force      # Clear folder without confirmation

Safety:
  - Modifying commands show a warning to export bookmarks first
  - 'delete' and 'clear' require confirmation (use -y/--force to skip)
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
    p_list = subparsers.add_parser("list", help="List all bookmarks")
    p_list.add_argument("--depth", type=int, help="Maximum depth to display")
    
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
        
        # Afficher l'avertissement pour les commandes qui modifient les favoris
        if args.action in MODIFYING_COMMANDS:
            print_safety_warning(manager.browser_name)
        
        if args.action == "list":
            manager.list_all(max_depth=args.depth)
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
            # Confirmation requise pour delete
            if args.force or confirm_action(f"Voulez-vous vraiment supprimer '{args.name}' ?"):
                manager.delete_item(args.name)
            else:
                print("❌ Opération annulée.")
        elif args.action == "clear":
            # Confirmation requise pour clear
            if args.force or confirm_action(f"Voulez-vous vraiment VIDER le dossier '{args.folder}' ? Cette action est IRRÉVERSIBLE !"):
                manager.clear_folder(args.folder)
            else:
                print("❌ Opération annulée.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
