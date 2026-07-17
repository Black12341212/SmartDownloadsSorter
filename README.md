# Smart Downloads Sorter v2.0

**Full automation, cloud integration, undo, duplicate detection and a clean GUI.**

Version 2.0 is a complete rewrite with a modular architecture, 15 new features, and a graphical interface built with tkinter.

---

## Features

### Core
- **Smart Sorting** - Files are sorted by extension, name patterns, regex, and size
- **PDF Intelligence** - Smart classification of PDFs (books, articles, forms, scans)
- **Silent Mode** - `python sorter.py --sort` for scripts and automation
- **Auto-Sort Scheduler** - `python sorter.py --auto 15` or GUI toggle (every N minutes)
- **Date Sorting** - Optional `YYYY-MM` subfolders based on download date
- **Ignore List** - Patterns to skip (`.tmp`, `Thumbs.db`, `*.crdownload`, etc.)

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
Tabbed interface with: Sort, Rules, History, Schedule, Stats, Duplicates, Settings, About.

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
python sorter.py --version                # Show version
```

---

## Project Structure

```
SmartSorter/
  sorter.py                    # Entry point (CLI + GUI launcher)
  requirements.txt             # Dependencies
  core/
    sorter_engine.py           # Sorting engine
    rules_manager.py           # Rules CRUD
    file_matcher.py            # File matching logic
    logger.py                  # Logging to sorter.log
    history.py                 # Undo system
    ignore_list.py             # Exclusion patterns
    duplicates.py              # Duplicate detection
    scheduler.py               # Auto-sort timer
    cloud_sync.py              # Cloud folder sync
    profiles.py                # Profile export/import
    plugin_loader.py           # Plugin system
    autostart.py               # Windows startup
  gui/
    app.py                     # Main window
    tray_icon.py               # System tray
    tabs/
      main_tab.py              # Sort tab
      rules_tab.py             # Rules editor
      history_tab.py           # Undo tab
      schedule_tab.py          # Scheduler tab
      stats_tab.py             # Statistics tab
      duplicates_tab.py        # Duplicates tab
      settings_tab.py          # Settings
      about_tab.py             # About + QR + Donate
  plugins/
    example_photo_meta.py      # Example plugin
  config/
    settings.json              # App settings
    rules.json                 # Sorting rules
    history.json               # Move history
    ignore_list.json           # Ignore patterns
    profiles/                  # Saved profiles
```

---

## Install & Run

```bash
pip install -r requirements.txt
python sorter.py
```

To build as `.exe`:
```bash
pip install pyinstaller
pyinstaller --onefile --name SmartSorter sorter.py
```

---

## Screenshots

<img width="902" height="682" alt="image" src="https://github.com/user-attachments/assets/88a3980d-6fb7-4b7c-8317-d4d3546ae4fd" />
<img width="902" height="682" alt="image" src="https://github.com/user-attachments/assets/122f759c-80c7-4f00-b76e-66da0162cf0c" />
<img width="902" height="682" alt="image" src="https://github.com/user-attachments/assets/466e10ab-d856-4045-abbd-d3fb88998aee" />
<img width="902" height="682" alt="image" src="https://github.com/user-attachments/assets/3ad1ffcd-e360-4877-9088-0281c0257604" />
<img width="902" height="682" alt="image" src="https://github.com/user-attachments/assets/4acf1ffe-e7cc-4355-a1d1-209349b93da6" />
