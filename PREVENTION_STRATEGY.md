# VS Code Auto-Restore Prevention Strategy

## The Problem
VS Code has been automatically restoring deleted files when the workspace is reopened. This happens because:

1. **VS Code Cache**: VS Code maintains internal caches of workspace files
2. **Git Integration**: VS Code may restore files from git history or staging area
3. **Workspace State**: VS Code saves and restores workspace state including open files
4. **File Watchers**: VS Code file watchers may recreate "missing" files

## Comprehensive Solution

### 1. Git-Based Cleanup (Primary Method)
Use git commands to permanently remove files from tracking:

```powershell
# Run the PowerShell cleanup script
.\permanent_cleanup.ps1

# Or manually:
git rm --cached file_to_remove.py
git rm -r --cached directory_to_remove/
git commit -m "Remove temporary files"
```

### 2. VS Code Configuration
Create `.vscode/settings.json` with exclusion rules:

```json
{
  "files.watcherExclude": {
    "**/test_*.py": true,
    "**/demo_*.py": true,
    "**/*_demo.py": true,
    "**/debug_*.py": true,
    "**/analyze_*.py": true,
    "**/cleanup_*.py": true,
    "**/*.bat": true,
    "**/*.ps1": true,
    "**/analysis/**": true,
    "**/batch/**": true,
    "**/archive/**": true
  },
  "files.exclude": {
    "**/test_*.py": true,
    "**/demo_*.py": true,
    "**/*_demo.py": true,
    "**/debug_*.py": true
  },
  "search.exclude": {
    "**/test_*.py": true,
    "**/demo_*.py": true,
    "**/*_demo.py": true,
    "**/debug_*.py": true,
    "**/analyze_*.py": true,
    "**/cleanup_*.py": true
  }
}
```

### 3. Enhanced .gitignore
Add comprehensive ignore patterns:

```gitignore
# === WORKSPACE CLEANUP PROTECTION ===
# Prevent VS Code auto-restore of unwanted files

# Development and testing files (root level only)
/test_*.py
/demo_*.py
/*_demo.py
/debug_*.py
/temp_*.py
/tmp_*.py

# Analysis and diagnostic files
/analyze_*.py
/check_*.py
/fix_*.py
/diagnose_*.py
/investigate_*.py
/verify_*.py
/validate_*.py

# Cleanup and maintenance files
/cleanup_*.py
/clear_*.py
/emergency_*.py
/force_*.py
/reset_*.py
/restart_*.py
/move_*.py

# Legacy and outdated files
/legacy_*.py
/scalping_bot.py
/intraday_trading_bot.py
/main_simple.py
/minimal_main.py

# Duplicate dashboards
/dashboard.py
/dashboard_enhanced.py
/live_dashboard.py

# Batch and script files
*.bat
*.ps1
*.sh

# Analysis summaries and guides (excessive)
/*_SUMMARY.md
/*_GUIDE.md
/*_ANALYSIS.md
/*_COMPLETE.md
/*_FIX*.md

# Temporary directories
/analysis/
/batch/
/archive/
/demo_reports/

# Backup files
cleanup_backup_list.json
```

## How to Restore Workspace to Last Cleanup

### Method 1: Run Automated Scripts
```powershell
# Option A: PowerShell script (Windows)
.\permanent_cleanup.ps1

# Option B: Python script (Cross-platform)
python permanent_cleanup.py
```

### Method 2: Manual Git Commands
```powershell
# Remove specific patterns from git
git rm --cached test_*.py
git rm --cached demo_*.py
git rm --cached debug_*.py
git rm --cached analyze_*.py
git rm --cached cleanup_*.py
git rm --cached legacy_*.py
git rm --cached scalping_bot.py
git rm --cached dashboard*.py
git rm -r --cached analysis/
git rm -r --cached batch/
git rm -r --cached archive/

# Commit the removals
git commit -m "Clean workspace - remove temporary files"

# Physically delete files
Remove-Item test_*.py, demo_*.py, debug_*.py, analyze_*.py -Force
Remove-Item cleanup_*.py, legacy_*.py, scalping_bot.py -Force
Remove-Item dashboard*.py -Force
Remove-Item -Recurse analysis/, batch/, archive/ -Force
```

### Method 3: Hard Reset (Nuclear Option)
```powershell
# Only if other methods fail
git reset --hard HEAD~1  # Go back one commit
git clean -fd            # Remove untracked files and directories
```

## Prevention Checklist

### ✅ Before Making Changes
- [ ] Run cleanup script to establish clean baseline
- [ ] Verify .gitignore is updated
- [ ] Verify VS Code settings are configured
- [ ] Commit clean state to git

### ✅ After Cleanup
- [ ] Restart VS Code completely
- [ ] Verify files are not visible in Explorer
- [ ] Verify files are not in git tracking (`git status`)
- [ ] Test opening/closing workspace doesn't restore files

### ✅ Regular Maintenance
- [ ] Run cleanup script weekly if needed
- [ ] Monitor for new temporary files
- [ ] Update .gitignore patterns if new file types appear
- [ ] Keep VS Code updated (newer versions may handle this better)

## Why This Works

1. **Git Removal**: Removes files from git tracking so VS Code can't restore from repository
2. **Physical Deletion**: Removes actual files from filesystem
3. **VS Code Configuration**: Tells VS Code to ignore these file patterns completely
4. **.gitignore**: Prevents future tracking of similar files
5. **Commit Process**: Makes the cleanup permanent in git history

## Emergency Recovery

If the automated cleanup removes something important:

```powershell
# Check what was removed
Get-Content cleanup_backup_list.json

# Restore from git if needed
git checkout HEAD~1 -- important_file.py

# Or restore from backup if you made one
```

## Files That Will Never Be Removed

The cleanup scripts protect these essential files:
- `launcher.py`
- `main.py`
- `config.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- All files in `core/`, `strategies/`, `utils/`, `docs/` directories
- All configuration files (`.env`, `pytest.ini`, etc.)

## Troubleshooting

### If Files Keep Reappearing:
1. Ensure VS Code is completely closed during cleanup
2. Run cleanup script as administrator
3. Clear VS Code workspace state: Delete `.vscode/` folder temporarily
4. Update VS Code to latest version
5. Check for VS Code extensions that might be recreating files

### If Git Commands Fail:
1. Ensure you're in the correct directory
2. Check git status: `git status`
3. Ensure git is initialized: `git init` if needed
4. Stage files first: `git add .` before committing

This strategy combines multiple approaches to ensure files stay deleted and prevents VS Code from auto-restoring them.
