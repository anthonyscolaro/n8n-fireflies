#!/bin/bash
# Repository Optimization Script
# Run this before committing to ensure fast uploads

echo "🔍 Checking for large files that might slow down git pushes..."

# Find files larger than 1MB
echo "Files larger than 1MB:"
find . -type f -size +1M -not -path "./.git/*" -not -path "./scripts/fireflies/fireflies_export.jsonl" | head -10

# Check total repo size (excluding .git)
echo -e "\n📊 Repository size breakdown:"
du -sh */ 2>/dev/null | sort -hr

# Check for common large file types that should be gitignored
echo -e "\n⚠️  Checking for potentially large files:"
find . -name "*.jsonl" -o -name "*.csv" -o -name "*.sqlite" -o -name "*.db" -o -name "*.zip" | grep -v .git | head -5

# Suggest optimization
echo -e "\n💡 Optimization tips:"
echo "- Data files (*.jsonl, *.csv) should go in scripts/fireflies/data/ (gitignored)"
echo "- Use external storage (S3, Google Drive) for large datasets"
echo "- Compress files before committing if they must be tracked"
echo "- Consider Git LFS for files that must be version controlled"

echo -e "\n✅ Run 'git status' to see what will be committed" 