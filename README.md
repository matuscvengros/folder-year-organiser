# disk-date-separator
Quick utility that separates disks filled with various files into separate years with the same folder structure.

## Description

This Python script recursively searches a directory and organizes files by their creation year. Files are moved into year-based subdirectories at the root level, while preserving the original directory structure within each year folder.

## Features

- Recursively processes all files in a directory
- Organizes files by creation year
- Preserves original directory structure within year folders
- Automatically cleans up empty directories after moving files
- Dry-run mode to preview changes before executing
- Skips already-organized year directories

## Requirements

- Python 3.6+
- No external dependencies required

## Installation

Simply clone this repository or download the `disk_date_separator.py` script.

## Usage

### Basic usage:
```bash
python3 disk_date_separator.py /path/to/directory
```

### Dry-run (preview without making changes):
```bash
python3 disk_date_separator.py /path/to/directory --dry-run
```

### Organize current directory:
```bash
python3 disk_date_separator.py .
```

## Example

Given a directory structure like:
```
my_files/
├── photos/
│   ├── photo1.jpg (created in 2022)
│   └── vacation/
│       └── photo2.jpg (created in 2023)
└── documents/
    └── report.pdf (created in 2023)
```

After running `python3 disk_date_separator.py my_files/`, the structure becomes:
```
my_files/
├── 2022/
│   └── photos/
│       └── photo1.jpg
└── 2023/
    ├── photos/
    │   └── vacation/
    │       └── photo2.jpg
    └── documents/
        └── report.pdf
```

## Options

- `directory` (positional, required): The directory to organize
- `--dry-run` (optional): Preview changes without moving files
- `--help`: Show help message

## Notes

- The script uses file creation time on Windows and macOS
- On Linux, it falls back to modification time if creation time is not available
- Year directories (4-digit numeric directories at root level) are automatically skipped to prevent re-processing already organized files
- Empty directories are automatically removed after files are moved
