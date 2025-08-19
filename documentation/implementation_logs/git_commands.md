# 🔧 Git Commands for Trading Bot Management

## 🔍 **Check Current Git Status**
```powershell
git status
```
*Shows all modified (M) and untracked (U) files*

## 📋 **See What's Changed**
```powershell
git diff
```
*Shows the actual changes in modified files*

## ➕ **Add Files to Tracking**

**Add a specific file:**
```powershell
git add stock_specific_config.py
```

**Add all untracked files:**
```powershell
git add .
```

**Add only modified files (not new ones):**
```powershell
git add -u
```

## 💾 **Commit Your Changes**

**Commit with a message:**
```powershell
git commit -m "Updated stock-specific thresholds and risk management"
```

**Add and commit in one step:**
```powershell
git commit -am "Quick update to trading parameters"
```

## 🚀 **Push to GitHub**
```powershell
git push origin main
```

## 🔄 **Complete Workflow Example**
```powershell
# Check what's changed
git status

# Add all your trading bot changes
git add .

# Commit with descriptive message
git commit -m "Enhanced trading system with stock-specific thresholds and trailing stops"

# Push to GitHub
git push origin main
```

## 🎯 **Quick One-Liners for Your Trading Bot**

**Add and commit current work:**
```powershell
git add . ; git commit -m "Trading bot updates - $(Get-Date -Format 'yyyy-MM-dd')"
```

**Complete backup to GitHub:**
```powershell
git add . ; git commit -m "Daily trading system backup" ; git push origin main
```

## ⚡ **Pro Tip**
You can also use **Option 11** in your launcher.py - it automatically handles the Git backup process for you!

## 🔍 **Additional Useful Commands**

**View commit history:**
```powershell
git log --oneline
```

**See changes in a specific file:**
```powershell
git diff stock_specific_config.py
```

**Undo changes to a file (before staging):**
```powershell
git checkout -- filename.py
```

**Remove file from staging:**
```powershell
git reset HEAD filename.py
```

**Create and switch to new branch:**
```powershell
git checkout -b new-feature-branch
```

**Switch between branches:**
```powershell
git checkout main
git checkout feature-branch
```

## 🛡️ **Safety Commands**

**Stash current changes (temporary save):**
```powershell
git stash
```

**Restore stashed changes:**
```powershell
git stash pop
```

**View what would be committed:**
```powershell
git diff --staged
```

---

*These commands will help you manage your trading bot code changes and keep everything properly tracked in Git.*
