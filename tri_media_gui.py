import os
import shutil
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, UnidentifiedImageError
import exifread
from dateutil import parser

# =========================
# CONFIG
# =========================

CATEGORIES = {
    "Photos": [".jpg", ".jpeg", ".png", ".heic", ".webp"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Musiques": [".mp3", ".wav", ".flac", ".aac"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"]
}

SYSTEM_FILES = [".ds_store"]
TEMP_FILES = [".tmp", ".log"]
THUMB_FILES = ["thumbs.db"]

# =========================
# UTILS
# =========================

def get_category(ext):
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Autres"

def get_date_from_exif(filepath):
    try:
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            date_str = str(tags.get("EXIF DateTimeOriginal"))
            return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None

def get_date_from_image(filepath):
    try:
        img = Image.open(filepath)
        exif = img._getexif()
        if exif:
            date = exif.get(36867)
            if date:
                return datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
    except UnidentifiedImageError:
        return None
    except Exception:
        return None
    return None

def get_date_from_filename(filename):
    try:
        return parser.parse(filename, fuzzy=True)
    except Exception:
        return None

def get_file_date(filepath):
    date = get_date_from_exif(filepath)
    if not date:
        date = get_date_from_image(filepath)
    if not date:
        date = get_date_from_filename(os.path.basename(filepath))
    if not date:
        timestamp = os.path.getmtime(filepath)
        date = datetime.fromtimestamp(timestamp)
    return date

def file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

# =========================
# PROCESS FILE
# =========================

def process_file(filepath, source_dir, dest_dir, detect_duplicates, hash_cache, lock):
    file = os.path.basename(filepath)
    ext = os.path.splitext(file)[1].lower()

    try:
        # Doublons
        if detect_duplicates:
            h = file_hash(filepath)
            if h:
                with lock:
                    if h in hash_cache:
                        return False, f"[DUPLICATE] {file}"
                    hash_cache.add(h)

        category = get_category(ext)

        try:
            date = get_file_date(filepath)
            year = str(date.year)
            month = f"{date.month:02d}"
        except Exception as e:
            return False, f"[DATE ERROR] {file} | {type(e).__name__}: {e}"

        dest_path = os.path.join(dest_dir, category, year, month)
        os.makedirs(dest_path, exist_ok=True)

        dest_file = os.path.join(dest_path, file)

        # éviter overwrite
        if os.path.exists(dest_file):
            base, ext2 = os.path.splitext(file)
            i = 1
            while os.path.exists(dest_file):
                dest_file = os.path.join(dest_path, f"{base}_{i}{ext2}")
                i += 1

        try:
            shutil.copy2(filepath, dest_file)
        except Exception as e:
            return False, f"[COPY ERROR] {file} | {type(e).__name__}: {e}"

        return True, f"{file} → {category}/{year}/{month}"

    except Exception as e:
        return False, f"[GENERAL ERROR] {file} | {type(e).__name__}: {e}"

# =========================
# GUI
# =========================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Tri automatique fichiers")

        self.source = tk.StringVar()
        self.dest = tk.StringVar()

        tk.Label(root, text="Dossier source").pack()
        tk.Entry(root, textvariable=self.source, width=50).pack()
        tk.Button(root, text="Choisir", command=self.select_source).pack()

        tk.Label(root, text="Dossier destination").pack()
        tk.Entry(root, textvariable=self.dest, width=50).pack()
        tk.Button(root, text="Choisir", command=self.select_dest).pack()

        # Filtres
        tk.Label(root, text="Filtres").pack()

        self.ignore_system = tk.BooleanVar(value=True)
        self.ignore_temp = tk.BooleanVar(value=True)
        self.ignore_thumbs = tk.BooleanVar(value=True)

        tk.Checkbutton(root, text="Fichiers système (.DS_Store)", variable=self.ignore_system).pack(anchor="w")
        tk.Checkbutton(root, text="Fichiers temporaires (.tmp, .log)", variable=self.ignore_temp).pack(anchor="w")
        tk.Checkbutton(root, text="Miniatures (thumbs.db)", variable=self.ignore_thumbs).pack(anchor="w")

        # Doublons
        self.detect_duplicates = tk.BooleanVar(value=False)
        tk.Checkbutton(root, text="Détection des doublons (lent)", variable=self.detect_duplicates).pack(anchor="w")

        self.progress = ttk.Progressbar(root, length=400)
        self.progress.pack(pady=10)

        self.log = tk.Text(root, height=12)
        self.log.pack()

        tk.Button(root, text="Lancer", command=self.start).pack(pady=10)

    def select_source(self):
        self.source.set(filedialog.askdirectory())

    def select_dest(self):
        self.dest.set(filedialog.askdirectory())

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        source_dir = self.source.get()
        dest_dir = self.dest.get()

        detect_duplicates = self.detect_duplicates.get()

        files = []
        ignored = 0

        for root_dir, _, filenames in os.walk(source_dir):
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                name = f.lower()

                if self.ignore_system.get() and name in SYSTEM_FILES:
                    ignored += 1
                    continue

                if self.ignore_temp.get() and ext in TEMP_FILES:
                    ignored += 1
                    continue

                if self.ignore_thumbs.get() and name in THUMB_FILES:
                    ignored += 1
                    continue

                files.append(os.path.join(root_dir, f))

        self.log_msg(f"{ignored} fichiers ignorés")

        total = len(files)
        self.progress["maximum"] = total

        hash_cache = set()
        lock = threading.Lock()

        def update_progress():
            self.progress["value"] += 1

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(process_file, f, source_dir, dest_dir, detect_duplicates, hash_cache, lock)
                for f in files
            ]

            for future in futures:
                success, msg = future.result()
                if success:
                    self.log_msg(f"✔ {msg}")
                else:
                    self.log_msg(f"❌ {msg}")
                self.root.after(0, update_progress)

        self.log_msg("✅ Terminé !")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()