# Smart Downloads Sorter v3.0

**Full automation, cloud integration, undo, duplicate detection, real-time monitoring, and a clean GUI.**

Version 3.0 adds 18 new features: real-time file monitoring, multi-folder support, content-based detection, AI rule suggestions, auto-cleanup, drag & drop, regex tester, dark theme, backup/restore, keyboard shortcuts, file preview, nested rules, notifications, logging dashboard, portable mode, i18n, scheduled cleanup, and cloud API stubs.

---

## Features

### Core
- **Smart Sorting** - Files are sorted by extension, name patterns, regex, and size
- **PDF Intelligence** - Smart classification of PDFs (books, articles, forms, scans)
- **Silent Mode** - `python sorter.py --sort` for scripts and automation
- **Auto-Sort Scheduler** - `python sorter.py --auto 15` or GUI toggle (every N minutes)
- **Date Sorting** - Optional `YYYY-MM` subfolders based on download date
- **Ignore List** - Patterns to skip (`.tmp`, `Thumbs.db`, `*.crdownload`, etc.)

### New in v3.0

#### 1. Filesystem Watcher (real-time sorting)
Monitors folders for new files and sorts them instantly without waiting for the timer. Uses `watchdog` when available, falls back to polling.

#### 2. Multi-Folder Support
Sort multiple folders simultaneously. Specify comma-separated paths in Settings or via the `monitored_folders` option.

#### 3. Content-based Classification
Detects the real file type by reading magic bytes, not just the extension. A `.txt` that is actually a CSV, or a file with no extension that is an image -- both handled correctly.

#### 4. AI-powered Rule Suggestions
Analyzes move history to suggest new rules. If you frequently move "1C" files to "Documents/1C", it will propose a rule automatically.

#### 5. Auto-cleanup / Retention Policy
Automatically delete old files (e.g., installers older than 30 days). Configurable per-folder and per-extension.

#### 6. Drag & Drop
Drag files directly into the Sort tab for manual sorting by existing rules.

#### 7. Regex Tester
Built-in regex tester popup in the Rules tab. Test patterns before applying them to rules.

#### 8. Dark Theme
Full dark theme support with a toggle in Settings. Also supports light and default themes.

#### 9. Backup / Restore
Export all configuration (rules + settings + ignore list + profiles) to a single ZIP file. Restore with one click.

#### 10. Keyboard Shortcuts
- **Ctrl+S** -- Sort Now
- **Ctrl+Z** -- Undo Last
- **Ctrl+D** -- Dry Run
- **Ctrl+R** -- Refresh current tab
- **F5** -- Sort Now
- **Ctrl+Q** -- Quit

#### 11. File Preview
Preview file content (images, text, metadata) before moving. Drag & drop shows a preview dialog with file details.

#### 12. Nested / Conditional Rules
AND/OR logic for complex rules. Example: if PDF AND size > 5MB AND name contains "book" -> Books, ELSE if contains "scan" -> Scans.

#### 13. Notification System
System tray and in-app notifications after sorting (files moved, errors, cleanup results).

#### 14. Logging Dashboard
New "Logs" tab with real-time log viewing, level filtering (DEBUG/INFO/WARNING/ERROR), and auto-refresh.

#### 15. Portable Mode
Run from USB drive -- all configs stored next to the exe. Enable via `--portable` flag or Settings checkbox.

#### 16. I18n (Internationalization)
Full English and Russian interface with language switcher in Settings. 143 translated strings.

#### 17. Scheduled Cleanup
Weekly cleanup task (e.g., every Monday at 3 AM). Configurable day and target folders.

#### 18. Cloud API Stubs
UI placeholders for Google Drive, OneDrive, Dropbox integration (API tokens ready for future implementation).

### History & Undo
- **Undo** - `python sorter.py --undo 3` or GUI button. All moves recorded in `history.json`
- **Session Undo** - Undo an entire sorting session at once

### Analysis
- **Duplicate Detection** - Find files by name+size or MD5 hash, suggest cleanup
- **Statistics** - File count, total size, breakdown by extension

### Cloud & Automation
- **Cloud Sync** - Point to OneDrive/Dropbox folder, select which categories sync
- **Auto-Start** - Register in Windows startup via checkbox
- **System Tray** - pystray icon with quick actions (requires `pystray`)

### Profiles & Plugins
- **Profiles** - Export/Import rule sets (Work, Home, Media)
- **Plugins** - Drop Python scripts in `plugins/` folder for custom logic

### GUI (tkinter)
Tabbed interface with: Sort, Rules, History, Schedule, Stats, Duplicates, Logs, Settings, About.

The **About** tab includes a QR code linking to [donationalerts.com/r/zenixx5678](https://www.donationalerts.com/r/zenixx5678) and a non-intrusive "Support Project" button in the status bar.

---

## CLI Usage

```
python sorter.py                          # Launch GUI
python sorter.py --sort                   # Silent sort of Downloads
python sorter.py --sort --target D:\Files # Sort specific folder
python sorter.py --sort --dry-run         # Preview without moving
python sorter.py --auto 30                # Auto-sort every 30 min
python sorter.py --undo 3                 # Undo last 3 moves
python sorter.py --duplicates             # Find duplicate files
python sorter.py --duplicates --hash      # Hash-based duplicate scan
python sorter.py --backup                 # Create config backup
python sorter.py --restore backup.zip     # Restore from backup
python sorter.py --portable               # Run in portable mode
python sorter.py --version                # Show version
```

---

## Project Structure

```
SmartSorter/
  sorter.py                    # Entry point (CLI + GUI launcher)
  requirements.txt             # Dependencies
  core/
    sorter_engine.py           # Sorting engine (multi-folder, content detection)
    rules_manager.py           # Rules CRUD + nested rules
    file_matcher.py            # File matching logic + nested conditions + regex tester
    content_detector.py        # Magic-byte content detection
    logger.py                  # Logging to sorter.log + log reader
    history.py                 # Undo system
    ignore_list.py             # Exclusion patterns
    duplicates.py              # Duplicate detection
    scheduler.py               # Auto-sort timer + cleanup scheduler
    cloud_sync.py              # Cloud folder sync + settings manager
    profiles.py                # Profile export/import
    plugin_loader.py           # Plugin system
    autostart.py               # Windows startup
    portable.py                # Portable mode (USB/EXE)
    i18n.py                    # Internationalization (EN/RU)
    watcher.py                 # Filesystem watcher (real-time)
    retention.py               # Auto-cleanup / retention policy
    notifications.py           # Notification system
    backup.py                  # Backup / restore configuration
    ai_suggester.py            # AI-powered rule suggestions
  gui/
    app.py                     # Main window (themes, shortcuts, i18n)
    themes.py                  # Dark/Light theme definitions
    tray_icon.py               # System tray
    tabs/
      main_tab.py              # Sort tab (drag & drop, file preview)
      rules_tab.py             # Rules editor (regex tester, nested rules)
      history_tab.py           # Undo tab
      schedule_tab.py          # Scheduler + cleanup tab
      stats_tab.py             # Statistics tab
      duplicates_tab.py        # Duplicates tab
      logging_tab.py           # Log viewer (real-time, level filter)
      settings_tab.py          # Settings (all v3.0 options)
      about_tab.py             # About + QR + Donate
  plugins/
    example_photo_meta.py      # Example plugin
  config/
    settings.json              # App settings
    rules.json                 # Sorting rules
    history.json               # Move history
    ignore_list.json           # Ignore patterns
    profiles/                  # Saved profiles
    translations/              # Custom translation overrides
```

---

## Install & Run

```bash
pip install -r requirements.txt
python sorter.py
```

### Dependencies
- **Python 3.8+**
- `pystray` -- system tray icon (optional)
- `Pillow` -- QR code + image previews (optional)
- `watchdog` -- real-time filesystem monitoring (optional, falls back to polling)

### Portable Mode
```bash
python sorter.py --portable       # Enable portable mode via CLI
# Or create a .portable file in the app directory
```

### Backup / Restore
```bash
python sorter.py --backup                          # Create backup
python sorter.py --backup --output my_backup.zip   # Custom path
python sorter.py --restore my_backup.zip           # Restore
```

To build as `.exe`:
```bash
pip install pyinstaller
pyinstaller --onefile --name SmartSorter sorter.py
```

---