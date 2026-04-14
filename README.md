# File-ter

**File-ter** est une application de bureau Python qui trie automatiquement des fichiers depuis un dossier source vers un dossier de destination structuré, organisé par catégorie, année et mois. Elle dispose d'une interface graphique (GUI) simple construite avec Tkinter.

---

## Fonctionnalités

- **Catégorisation automatique** — les fichiers sont répartis dans `Photos`, `Videos`, `Musiques`, `Documents` ou `Autres`.
- **Organisation par date** — l'arborescence de destination suit le schéma `Catégorie/Année/Mois/`, avec la date résolue selon l'ordre de priorité suivant :
  1. Métadonnées EXIF (tag `DateTimeOriginal`)
  2. Données EXIF via PIL
  3. Date extraite du nom de fichier
  4. Date de modification du fichier (solution de repli)
- **Détection des doublons** — déduplication optionnelle par MD5 ; les fichiers identiques à un fichier déjà traité sont ignorés.
- **Filtres configurables** — ignorer indépendamment les fichiers système (`.DS_Store`), les fichiers temporaires (`.tmp`, `.log`) et les fichiers de miniatures (`thumbs.db`).
- **Traitement multi-threadé** — les fichiers sont copiés en parallèle grâce à un pool de 8 threads pour un tri plus rapide.
- **Suivi en temps réel** — une barre de progression et un journal déroulant affichent les résultats au fur et à mesure.

---

## Types de fichiers pris en charge

| Catégorie  | Extensions                              |
|------------|-----------------------------------------|
| Photos     | `.jpg` `.jpeg` `.png` `.heic` `.webp`   |
| Videos     | `.mp4` `.mov` `.avi` `.mkv`             |
| Musiques   | `.mp3` `.wav` `.flac` `.aac`            |
| Documents  | `.pdf` `.docx` `.txt` `.xlsx`           |
| Autres     | tout le reste                           |

---

## Structure de sortie

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

Si un fichier portant le même nom existe déjà à la destination, un suffixe numérique (`_1`, `_2`, …) est ajouté automatiquement pour éviter tout écrasement.

---

## Prérequis

- Python 3.8+
- [Pillow](https://python-pillow.org/) — traitement d'images et lecture EXIF
- [exifread](https://pypi.org/project/ExifRead/) — extraction robuste des tags EXIF
- [python-dateutil](https://pypi.org/project/python-dateutil/) — analyse de dates dans les noms de fichiers

Installez les dépendances avec :

```bash
pip install Pillow exifread python-dateutil
```

---

## Utilisation

```bash
python tri_media_gui.py
```

1. Cliquez sur **Choisir** à côté de *Dossier source* et sélectionnez le dossier contenant les fichiers à trier.
2. Cliquez sur **Choisir** à côté de *Dossier destination* et sélectionnez l'endroit où les fichiers triés seront déposés.
3. Ajustez les cases à cocher selon vos besoins :
   - **Fichiers système** — ignorer les fichiers `.DS_Store`.
   - **Fichiers temporaires** — ignorer les fichiers `.tmp` et `.log`.
   - **Miniatures** — ignorer les fichiers `thumbs.db`.
   - **Détection des doublons** — activer la détection par MD5 (plus lent sur les grandes bibliothèques).
4. Cliquez sur **Lancer** pour démarrer le tri. La progression et les résultats par fichier s'affichent dans le journal.

> **Remarque :** Les fichiers sont **copiés**, pas déplacés. Le dossier source reste intact.

---

## Notes

- La détection des doublons peut ralentir significativement le traitement sur de grandes collections ; ne l'activez que si nécessaire.

# Remarque
Le projet a été codé par ChatGPT, la fiabilité n'est donc pas garantie (d'où la copie, vous permettant de rapidement vérifier que vous avez tout vos fichiers).
