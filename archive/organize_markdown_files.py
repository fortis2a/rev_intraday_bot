#!/usr/bin/env python3
"""
Organize Markdown Files into Docs Folder
Move scattered .md files from root into properly organized docs structure
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_markdown_files():
    """Organize markdown files into the docs folder with proper categorization"""
    
    print("📄 ORGANIZING MARKDOWN FILES INTO DOCS FOLDER")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define categorization for markdown files
    markdown_categories = {
        "system_reports": {
            "description": "System Status & Organization Reports",
            "files": [
                "ORGANIZATION_COMPLETE.md",
                "DASHBOARD_ORGANIZATION_COMPLETE.md", 
                "DATABASE_SYSTEM_COMPLETE.md",
                "OPTIMIZATION_REPORT.md"
            ]
        },
        "feature_updates": {
            "description": "Feature Updates & Enhancement Documentation",
            "files": [
                "DATE_PICKER_UPDATE.md",
                "DATE_RANGE_FIX_SUMMARY.md",
                "ALPACA_PNL_CORRECTED.md"
            ]
        },
        "guides": {
            "description": "User Guides & Documentation",
            "files": [
                "TRADING_ANALYTICS_GUIDE.md"
            ]
        },
        "root_docs": {
            "description": "Keep in Root - Essential Project Documentation",
            "files": [
                "README.md"  # README should stay in root
            ]
        }
    }
    
    # Check which files exist in root
    root_md_files = list(Path('.').glob('*.md'))
    existing_files = [f.name for f in root_md_files]
    
    print("CURRENT ROOT DIRECTORY MARKDOWN FILES:")
    print("-" * 40)
    for i, filename in enumerate(sorted(existing_files), 1):
        file_size = Path(filename).stat().st_size / 1024
        print(f"{i:2d}. {filename:<35} {file_size:>6.1f}KB")
    
    print(f"\nTotal: {len(existing_files)} markdown files in root")
    print()
    
    # Show proposed organization
    print("PROPOSED MARKDOWN ORGANIZATION:")
    print("=" * 80)
    
    total_files_to_move = 0
    organization_plan = {}
    
    for category_name, category_info in markdown_categories.items():
        if category_name == "root_docs":
            print(f"\n📁 ROOT/ - {category_info['description']}")
        else:
            print(f"\n📂 docs/{category_name.upper()}/ - {category_info['description']}")
        print("-" * 60)
        
        category_files = []
        for filename in category_info['files']:
            if filename in existing_files:
                file_size = Path(filename).stat().st_size / 1024
                status = "✅ FOUND"
                category_files.append(filename)
                if category_name != "root_docs":  # Don't count files staying in root
                    total_files_to_move += 1
            else:
                file_size = 0
                status = "❌ NOT FOUND"
            
            print(f"  {filename:<35} {file_size:>6.1f}KB  {status}")
        
        organization_plan[category_name] = category_files
    
    # Show files not in any category
    all_categorized_files = []
    for category_files in organization_plan.values():
        all_categorized_files.extend(category_files)
    
    uncategorized_files = [f for f in existing_files if f not in all_categorized_files]
    
    if uncategorized_files:
        print(f"\n📁 UNCATEGORIZED MARKDOWN FILES:")
        print("-" * 40)
        for filename in uncategorized_files:
            file_size = Path(filename).stat().st_size / 1024
            print(f"  {filename:<35} {file_size:>6.1f}KB  ❓ NEEDS CATEGORIZATION")
    
    print()
    print("MARKDOWN ORGANIZATION STRATEGY:")
    print("=" * 80)
    print("🎯 OBJECTIVE: Consolidate documentation in docs/ folder with logical structure")
    print()
    print("📋 PROPOSED ACTIONS:")
    
    for category_name, category_info in markdown_categories.items():
        category_files = organization_plan[category_name]
        if category_files:
            if category_name == "root_docs":
                print(f"   • KEEP IN ROOT: {len(category_files)} essential project files")
            else:
                print(f"   • CREATE docs/{category_name}/: {len(category_files)} {category_info['description'].lower()}")
    
    if uncategorized_files:
        print(f"   • REVIEW: {len(uncategorized_files)} uncategorized files need manual placement")
    
    print()
    print("🔍 ANALYSIS:")
    print(f"   • Total markdown files in root: {len(existing_files)}")
    print(f"   • Files to move to docs/: {total_files_to_move}")
    print(f"   • Files staying in root: {len(organization_plan.get('root_docs', []))}")
    print(f"   • New subdirectories to create: {len([c for c in markdown_categories.keys() if c != 'root_docs'])}")
    
    # Ask for confirmation
    print()
    response = input("📝 Proceed with markdown file organization? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Markdown organization cancelled by user")
        return False
    
    print()
    print("EXECUTING MARKDOWN ORGANIZATION:")
    print("=" * 80)
    
    # Ensure docs directory exists
    docs_dir = Path("docs")
    if not docs_dir.exists():
        docs_dir.mkdir()
        print(f"📁 CREATED: docs/")
    
    # Create subdirectories and move files
    moved_files = []
    created_dirs = []
    errors = []
    
    for category_name, category_files in organization_plan.items():
        if category_name == "root_docs":
            # Files staying in root
            print(f"📁 ROOT/ - Files staying in root directory")
            for filename in category_files:
                print(f"   ✅ KEEP: {filename}")
            continue
        
        if not category_files:
            continue
            
        # Create category subdirectory in docs
        category_dir = docs_dir / category_name
        if not category_dir.exists():
            category_dir.mkdir()
            created_dirs.append(f"docs/{category_name}")
            print(f"📁 CREATED: docs/{category_name}/")
        
        # Move files to category directory
        print(f"📂 DOCS/{category_name.upper()}/ - Moving {len(category_files)} files")
        
        for filename in category_files:
            source_path = Path(filename)
            dest_path = category_dir / filename
            
            try:
                shutil.move(str(source_path), str(dest_path))
                moved_files.append((filename, f"docs/{category_name}"))
                print(f"   ✅ MOVED: {filename} → docs/{category_name}/")
                
            except Exception as e:
                errors.append(f"{filename}: {e}")
                print(f"   ❌ ERROR: {filename} - {e}")
    
    # Handle uncategorized files - suggest placement
    if uncategorized_files:
        print(f"\n📁 UNCATEGORIZED FILES - Manual placement needed:")
        for filename in uncategorized_files:
            print(f"   ❓ {filename}")
            print(f"      Suggested: Move to docs/misc/ or categorize appropriately")
    
    # Create organization report
    print()
    print("FINAL MARKDOWN ORGANIZATION:")
    print("=" * 80)
    
    # Check final root directory
    final_root_md_files = list(Path('.').glob('*.md'))
    if final_root_md_files:
        print(f"📁 ROOT DIRECTORY: {len(final_root_md_files)} markdown files")
        for f in sorted(final_root_md_files, key=lambda x: x.name):
            size_kb = f.stat().st_size / 1024
            print(f"   📄 {f.name:<35} {size_kb:>6.1f}KB")
    else:
        print(f"📁 ROOT DIRECTORY: Clean - no markdown files except README")
    
    # Show docs directory structure
    if docs_dir.exists():
        print(f"\n📂 DOCS/ DIRECTORY STRUCTURE:")
        
        # Show root docs files
        root_docs_files = list(docs_dir.glob('*.md'))
        if root_docs_files:
            print(f"   📄 Root docs files: {len(root_docs_files)}")
            for f in sorted(root_docs_files, key=lambda x: x.name):
                size_kb = f.stat().st_size / 1024
                print(f"      📄 {f.name:<30} {size_kb:>6.1f}KB")
        
        # Show subdirectories
        for subdir in sorted(docs_dir.iterdir()):
            if subdir.is_dir():
                subdir_files = list(subdir.glob('*.md'))
                if subdir_files:
                    print(f"\n   📂 {subdir.name}/: {len(subdir_files)} files")
                    for f in sorted(subdir_files, key=lambda x: x.name):
                        size_kb = f.stat().st_size / 1024
                        print(f"      📄 {f.name:<30} {size_kb:>6.1f}KB")
    
    # Create summary report
    report_content = f"""# Markdown Organization Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Markdown files organized: {len(moved_files)}
- Directories created: {len(created_dirs)}
- Files remaining in root: {len(final_root_md_files)}
- Errors: {len(errors)}

## Organization Structure

### Root Directory
Essential project documentation that remains in root:
"""
    
    for f in sorted(final_root_md_files, key=lambda x: x.name):
        size_kb = f.stat().st_size / 1024
        report_content += f"- {f.name} ({size_kb:.1f}KB)\n"
    
    for category_dir_path in created_dirs:
        category_name = category_dir_path.split('/')[-1]
        category_files = list(Path(category_dir_path).glob('*.md'))
        if category_files:
            category_desc = markdown_categories[category_name]['description']
            report_content += f"\n### {category_dir_path}\n{category_desc}\n"
            for f in sorted(category_files, key=lambda x: x.name):
                size_kb = f.stat().st_size / 1024
                report_content += f"- {f.name} ({size_kb:.1f}KB)\n"
    
    if moved_files:
        report_content += f"\n## Files Moved\n"
        for filename, destination in moved_files:
            report_content += f"- {filename} → {destination}\n"
    
    if errors:
        report_content += f"\n## Errors\n"
        for error in errors:
            report_content += f"- {error}\n"
    
    # Save report to docs directory
    report_path = docs_dir / "markdown_organization_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print()
    print("MARKDOWN ORGANIZATION RESULTS:")
    print("=" * 80)
    print(f"✅ Successfully organized: {len(moved_files)} markdown files")
    print(f"📁 Directories created: {len(created_dirs)}")
    print(f"🏠 Files in root: {len(final_root_md_files)}")
    print(f"📋 Report saved: {report_path}")
    
    if len(moved_files) > 0:
        print()
        print("🎉 MARKDOWN ORGANIZATION COMPLETE!")
        print("=" * 80)
        print("🎯 RESULTS:")
        print(f"   📄 Documentation consolidated in docs/ folder")
        print(f"   🗂️ {len(created_dirs)} organized categories created")
        print(f"   📁 Clean root directory with only essential README")
        print(f"   📚 Logical documentation structure for easy navigation")
        print()
        print("🚀 YOUR DOCUMENTATION IS NOW PROFESSIONALLY ORGANIZED!")
        print("   - System reports grouped together")
        print("   - Feature updates documented separately") 
        print("   - User guides easily accessible")
        print("   - All documentation discoverable in docs/ folder")
    
    return len(moved_files) > 0

if __name__ == "__main__":
    try:
        success = organize_markdown_files()
        if success:
            print("\n🏆 MARKDOWN ORGANIZATION COMPLETED SUCCESSFULLY! 🏆")
        else:
            print("\n📝 Markdown organization cancelled or no changes made")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
