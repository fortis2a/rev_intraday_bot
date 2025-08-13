#!/bin/bash
#
# Automated GitHub Backup Script for Intraday Trading Bot (Bash version)
# Daily backup script that commits and pushes all changes to GitHub
#

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "🔄 Starting automated GitHub backup..."

# Check if git repository exists
if [ ! -d ".git" ]; then
    echo "❌ No git repository found. Run setup first."
    exit 1
fi

# Get current date and time
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
date=$(date '+%Y-%m-%d')

# Add all changes
echo "📁 Adding files to staging..."
git add .

# Check if there are changes to commit
changes=$(git diff --cached --name-only)
if [ -z "$changes" ]; then
    echo "✅ No changes to backup."
    exit 0
fi

echo "📝 Found changes in files:"
echo "$changes" | sed 's/^/   - /'

# Create commit message
commit_message="Daily backup [$date]

Auto-backup of intraday trading system:
- Configuration updates
- Trading logs and data
- Performance reports
- System improvements

Timestamp: $timestamp"

# Commit changes
echo "💾 Committing changes..."
git commit -m "$commit_message"

if [ $? -ne 0 ]; then
    echo "❌ Failed to commit changes."
    exit 1
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully backed up to GitHub!"
    echo "📊 Repository: https://github.com/ZEUS7916/intraday-trading-bot"
else
    echo "❌ Failed to push to GitHub. Check authentication."
    exit 1
fi

echo "🎯 Backup completed at $timestamp"
