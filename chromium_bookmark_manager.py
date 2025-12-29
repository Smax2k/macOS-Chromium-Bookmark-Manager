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
    
    def delete_item(self, name):
        """Delete a bookmark or folder by name."""
        # Search in bookmarks bar
        item = self.bookmarks_bar.get_bookmark(name)
        if item:
            item.delete()
            print(f"✅ Bookmark '{name}' deleted")
            return True
        
        folder = self.bookmarks_bar.get_folder(name)
        if folder:
            folder.delete()
            print(f"✅ Folder '{name}' deleted")
            return True
        
        # Search in other bookmarks
        item = self.other_bookmarks.get_bookmark(name)
        if item:
            item.delete()
            print(f"✅ Bookmark '{name}' deleted")
            return True
        
        folder = self.other_bookmarks.get_folder(name)
        if folder:
            folder.delete()
            print(f"✅ Folder '{name}' deleted")
            return True
        
        print(f"❌ '{name}' not found")
        return False


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


def main():
    parser = argparse.ArgumentParser(
        description="Chromium Bookmark Manager - Manage bookmarks for Chromium-based browsers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                           # List all bookmarks (default: Chrome)
  %(prog)s -b brave list                  # List bookmarks in Brave
  %(prog)s -b edge search "github"        # Search in Edge bookmarks
  %(prog)s add "GitHub" "https://github.com" --folder "Bookmarks Bar/Dev"
  %(prog)s browsers                       # Show supported browsers
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
    p_list.add_argument("--depth", type=int, help="Maximum depth")
    
    # search
    p_search = subparsers.add_parser("search", help="Search for a bookmark")
    p_search.add_argument("query", help="Search term")
    p_search.add_argument("--limit", type=int, default=50, help="Max results")
    
    # add
    p_add = subparsers.add_parser("add", help="Add a bookmark")
    p_add.add_argument("title", help="Bookmark title")
    p_add.add_argument("url", help="Bookmark URL")
    p_add.add_argument("--folder", help="Target folder path")
    
    # create_folder
    p_folder = subparsers.add_parser("create_folder", help="Create a folder")
    p_folder.add_argument("path", help="Folder path (e.g., 'Bookmarks Bar/New')")
    
    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a bookmark or folder")
    p_delete.add_argument("name", help="Name of the item to delete")
    
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
        
        if args.action == "list":
            manager.list_all(max_depth=args.depth)
        elif args.action == "search":
            results = manager.search(args.query, args.limit)
            if not results:
                print("No results found.")
            for r in results:
                print(r)
        elif args.action == "add":
            manager.add_bookmark(args.title, args.url, args.folder)
        elif args.action == "create_folder":
            manager.create_folder(args.path)
        elif args.action == "delete":
            manager.delete_item(args.name)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
