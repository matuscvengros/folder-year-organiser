#!/usr/bin/env python3
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


def get_file_creation_date(file_path):
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


def organize_files(source_dir, dry_run=False):
    """
    Organize files in source_dir by creation year.
    
    Args:
        source_dir: Root directory to organize
        dry_run: If True, only print what would be done without actually moving files
    """
    source_path = Path(source_dir).resolve()
    
    if not source_path.exists():
        print(f"Error: Directory '{source_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    if not source_path.is_dir():
        print(f"Error: '{source_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Organizing files in: {source_path}")
    if dry_run:
        print("DRY RUN: No files will be moved")
    
    # Collect all files first (to avoid issues with moving files during iteration)
    files_to_process = []
    
    for root, dirs, files in os.walk(source_path):
        root_path = Path(root)
        
        # Skip year directories at the root level (to avoid processing already organized files)
        # Modify dirs in-place to prevent os.walk from descending into them
        if root_path == source_path:
            dirs_to_skip = [d for d in dirs if d.isdigit() and len(d) == 4]
            for dir_name in dirs_to_skip:
                print(f"Skipping year directory: {dir_name}")
                dirs.remove(dir_name)
            
        for filename in files:
            file_path = root_path / filename
            files_to_process.append(file_path)
    
    print(f"Found {len(files_to_process)} files to process")
    
    # Process each file
    moved_count = 0
    error_count = 0
    
    for file_path in files_to_process:
        try:
            # Get creation date
            creation_date = get_file_creation_date(file_path)
            year = creation_date.year
            
            # Calculate relative path from source directory
            relative_path = file_path.relative_to(source_path)
            
            # Build new path: source_dir / year / relative_path
            year_dir = source_path / str(year)
            new_file_path = year_dir / relative_path
            
            # Skip if file is already in the correct location
            if file_path == new_file_path:
                continue
            
            print(f"Moving: {relative_path} -> {year}/{relative_path}")
            
            if not dry_run:
                # Create destination directory if it doesn't exist
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(file_path), str(new_file_path))
                
            moved_count += 1
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            error_count += 1
    
    print(f"\nCompleted!")
    print(f"Files processed: {moved_count}")
    if error_count > 0:
        print(f"Errors encountered: {error_count}")
    
    # Clean up empty directories
    if not dry_run:
        cleanup_empty_dirs(source_path)


def cleanup_empty_dirs(root_path):
    """
    Remove empty directories (except year directories and the root).
    
    Args:
        root_path: Root directory to clean up
    """
    for root, dirs, files in os.walk(root_path, topdown=False):
        root_dir = Path(root)
        
        # Don't remove the root directory or year directories at root level
        if root_dir == root_path:
            continue
        if root_dir.parent == root_path and root_dir.name.isdigit() and len(root_dir.name) == 4:
            continue
            
        # Try to remove directory if it's empty
        try:
            if not os.listdir(root_dir):
                print(f"Removing empty directory: {root_dir.relative_to(root_path)}")
                root_dir.rmdir()
        except OSError:
            pass


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Organize files by creation year while preserving directory structure.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/photos
  %(prog)s /path/to/photos --dry-run
  %(prog)s .
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory to organize (files will be organized into year subdirectories)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually moving files'
    )
    
    args = parser.parse_args()
    
    organize_files(args.directory, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
