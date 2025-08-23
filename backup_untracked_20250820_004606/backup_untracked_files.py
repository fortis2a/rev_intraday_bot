#!/usr/bin/env python3
"""
Backup Untracked Files Script
Creates a timestamped backup of all untracked files in the repository
"""

import os
import shutil
import subprocess
from datetime import datetime
import json


def get_untracked_files():
    """Get list of untracked files from git"""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        )
        untracked_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
        return untracked_files
    except subprocess.CalledProcessError as e:
        print(f"Error getting untracked files: {e}")
        return []


def create_backup_directory():
    """Create timestamped backup directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_untracked_{timestamp}"

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ Created backup directory: {backup_dir}")

    return backup_dir


def backup_file(src_path, backup_dir):
    """Backup a single file maintaining directory structure"""
    dest_path = os.path.join(backup_dir, src_path)
    dest_dir = os.path.dirname(dest_path)

    # Create destination directory if it doesn't exist
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    try:
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
            return True
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            return True
        else:
            print(f"⚠️ Warning: {src_path} does not exist or is not a file/directory")
            return False
    except Exception as e:
        print(f"❌ Error backing up {src_path}: {e}")
        return False


def create_backup_manifest(backup_dir, backed_up_files):
    """Create a manifest of backed up files"""
    manifest = {
        "backup_timestamp": datetime.now().isoformat(),
        "backup_directory": backup_dir,
        "total_files": len(backed_up_files),
        "files": backed_up_files,
    }

    manifest_path = os.path.join(backup_dir, "backup_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"📋 Created backup manifest: {manifest_path}")


def main():
    """Main backup function"""
    print("🔄 Starting Untracked Files Backup...")
    print("=" * 50)

    # Get current working directory
    cwd = os.getcwd()
    print(f"📁 Working Directory: {cwd}")

    # Get untracked files
    untracked_files = get_untracked_files()
    if not untracked_files:
        print("✅ No untracked files found!")
        return

    print(f"📊 Found {len(untracked_files)} untracked files/directories:")
    for file in untracked_files:
        print(f"   📄 {file}")

    print("\n" + "=" * 50)

    # Create backup directory
    backup_dir = create_backup_directory()

    # Backup each file
    backed_up_files = []
    failed_files = []

    for file_path in untracked_files:
        print(f"📦 Backing up: {file_path}")
        if backup_file(file_path, backup_dir):
            backed_up_files.append(file_path)
            print(f"   ✅ Success")
        else:
            failed_files.append(file_path)
            print(f"   ❌ Failed")

    print("\n" + "=" * 50)
    print("📋 BACKUP SUMMARY:")
    print(f"   ✅ Successfully backed up: {len(backed_up_files)} files")
    print(f"   ❌ Failed to backup: {len(failed_files)} files")
    print(f"   📁 Backup location: {backup_dir}")

    if failed_files:
        print(f"\n❌ Failed files:")
        for file in failed_files:
            print(f"   - {file}")

    # Create manifest
    create_backup_manifest(backup_dir, backed_up_files)

    print(f"\n🎉 Backup completed! Files saved to: {backup_dir}")


if __name__ == "__main__":
    main()
