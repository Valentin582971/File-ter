# File-ter

**File-ter** is a Python desktop application that automatically sorts files from a source folder into a structured destination folder, organised by category, year, and month. It features a simple graphical user interface (GUI) built with Tkinter.

---

## Features

- **Automatic categorisation** — files are sorted into `Photos`, `Videos`, `Musiques` (Music), `Documents`, or `Autres` (Others).
- **Date-aware organisation** — the destination folder tree follows the pattern `Category/Year/Month/`, with the date resolved from (in priority order):
  1. EXIF metadata (`DateTimeOriginal` tag)
  2. PIL image EXIF data
  3. Date embedded in the filename
  4. File modification time (fallback)
- **Duplicate detection** — optional MD5-based deduplication skips files that are identical to one already processed.
- **Configurable file filters** — independently ignore system files (`.DS_Store`), temporary files (`.tmp`, `.log`), and thumbnail files (`thumbs.db`).
- **Multi-threaded processing** — files are copied concurrently using a thread-pool (8 workers) for faster sorting.
- **Live progress feedback** — a progress bar and scrollable log display results in real time.

---

## Supported File Types

| Category   | Extensions                              |
|------------|-----------------------------------------|
| Photos     | `.jpg` `.jpeg` `.png` `.heic` `.webp`   |
| Videos     | `.mp4` `.mov` `.avi` `.mkv`             |
| Musiques   | `.mp3` `.wav` `.flac` `.aac`            |
| Documents  | `.pdf` `.docx` `.txt` `.xlsx`           |
| Autres     | everything else                         |

---

## Output Structure

```
destination/
├── Photos/
│   └── 2023/
│       └── 06/
│           └── photo.jpg
├── Videos/
│   └── 2022/
│       └── 12/
│           └── video.mp4
├── Musiques/
│   └── 2021/
│       └── 03/
│           └── song.mp3
└── Documents/
    └── 2024/
        └── 01/
            └── report.pdf
```

If a file with the same name already exists at the destination, a numeric suffix (`_1`, `_2`, …) is appended automatically to avoid overwriting.

---

## Requirements

- Python 3.8+
- [Pillow](https://python-pillow.org/) — image processing and EXIF reading
- [exifread](https://pypi.org/project/ExifRead/) — robust EXIF tag extraction
- [python-dateutil](https://pypi.org/project/python-dateutil/) — fuzzy date parsing from filenames

Install dependencies with:

```bash
pip install Pillow exifread python-dateutil
```

---

## Usage

```bash
python tri_media_gui.py
```

1. Click **Choisir** next to *Dossier source* and select the folder containing the files to sort.
2. Click **Choisir** next to *Dossier destination* and select where sorted files should be placed.
3. Adjust the filter checkboxes as needed:
   - **Fichiers système** — skip `.DS_Store` files.
   - **Fichiers temporaires** — skip `.tmp` and `.log` files.
   - **Miniatures** — skip `thumbs.db` files.
   - **Détection des doublons** — enable MD5 duplicate detection (slower for large libraries).
4. Click **Lancer** to start sorting. Progress and per-file results appear in the log window.

> **Note:** Files are **copied**, not moved. Your source folder is left untouched.

---

## Notes

- The GUI labels are in French; the application logic is language-independent.
- Very large collections may benefit from running duplicate detection only when necessary, as hashing every file adds processing time.

