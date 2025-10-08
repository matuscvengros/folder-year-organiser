#!/usr/bin python3
"""
disk-date-separator: A utility to organize files by creation year.

This script recursively searches a directory and organizes files into year-based
subdirectories while preserving the original directory structure within each year.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def file_creation_date(file_path: str) -> datetime:
    """
    Get the creation date of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        datetime object representing the file creation date
    """
    try:
        # Get file stats
        stat_info = os.stat(file_path)
        
        # On Windows, use st_ctime (creation time)
        # On Unix, st_ctime is the last metadata change time, so we use st_birthtime if available
        # Otherwise fall back to st_mtime (modification time)
        if hasattr(stat_info, 'st_birthtime'):
            # macOS and some BSD systems
            timestamp = stat_info.st_birthtime
        elif sys.platform == 'win32':
            # Windows
            timestamp = stat_info.st_ctime
        else:
            # Linux and others - use modification time as fallback
            timestamp = stat_info.st_mtime
            
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"Error getting creation date for {file_path}: {e}", file=sys.stderr)
        raise
    

def move_files(source_dir: str, copy: bool, dry_run: bool, full_path: bool) -> tuple[int, int]:
    """
    Move files to their respective year-based directories.

    Args:
        dry_run: If True, only print what would be done without actually moving files

    Returns:
        Tuple of (number of files moved, number of errors)
    """
    source_path = Path(source_dir).resolve()

    # Process each file
    moved_count = 0
    error_count = 0
    
    for root, _, files in os.walk(source_dir):
        root_path = Path(root)
                
        for filename in files:
            file_path = (root_path / filename).resolve()

            try:
                # Get creation date
                year = file_creation_date(file_path).year
                
                # Calculate relative path from parent of the source directory
                relative_path = file_path.relative_to(source_path.parent)
                
                # Build new path: year / source_dir / relative_path
                new_file_path = source_path.parent / str(year) / relative_path
                
                if not dry_run:
                    if full_path:
                        print(f"Moving: {file_path} -> {new_file_path}")
                    else:
                        print(f"Moving: {file_path.relative_to(source_path.parent)} -> {new_file_path.relative_to(source_path.parent)}")

                    # Create destination directory if it doesn't exist
                    new_file_path.parent.mkdir(parents=True, exist_ok=True)

                    if copy:
                        # Copy the file
                        shutil.copy2(str(file_path), str(new_file_path))
                    else:
                        # Move the file
                        shutil.move(str(file_path), str(new_file_path))
                    
                    moved_count += 1
                else:
                    if full_path:
                        print(f"[Dry Run] Would move: {file_path} -> {new_file_path}")
                    else:
                        print(f"[Dry Run] Would move: {file_path.relative_to(source_path.parent)} -> {new_file_path.relative_to(source_path.parent)}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                error_count += 1

    return moved_count, error_count


if __name__ == '__main__':
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Organize files by creation year while preserving directory structure.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=
        """
Examples:
%(prog)s /path/to/photos
%(prog)s /path/to/photos --dry-run
%(prog)s /path/to/photos --copy
%(prog)s
        """
    )
    
    parser.add_argument('directory', help='Directory to organize (files will be organized into year subdirectories)')
    parser.add_argument('--copy', action='store_true', help='Copy instead of move files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually moving files')
    parser.add_argument('--full-path', action='store_true', help='Show full paths in the output instead of relatives')
    args = parser.parse_args()
    
    moved_count, error_count = move_files(args.directory, args.copy, args.dry_run, args.full_path)

    print(f"\nJob completed!")
    print(f"Files processed: {moved_count}")
    if error_count > 0:
        print(f"Errors encountered: {error_count}")
