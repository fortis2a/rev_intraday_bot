#!/usr/bin/env python3
"""
Root Directory Individual Review - Comprehensive analysis of all remaining files
DETAILED ASSESSMENT - Review each file in the root directory for purpose and optimization
"""

import os
from datetime import datetime
from pathlib import Path


def analyze_root_directory():
    """Comprehensive analysis of all files in root directory"""

    print("ROOT DIRECTORY INDIVIDUAL REVIEW")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    root_path = Path(".")

    # Get all files (not just Python)
    all_files = [
        f for f in root_path.iterdir() if f.is_file() and not f.name.startswith(".")
    ]
    all_files.sort()

    # Categorize by file type
    python_files = [f for f in all_files if f.suffix == ".py"]
    batch_files = [f for f in all_files if f.suffix == ".bat"]
    config_files = [
        f for f in all_files if f.suffix in [".txt", ".ini", ".md", ".json"]
    ]
    other_files = [
        f for f in all_files if f not in python_files + batch_files + config_files
    ]

    print(f"TOTAL FILES IN ROOT: {len(all_files)}")
    print(f"  Python files (.py): {len(python_files)}")
    print(f"  Batch files (.bat): {len(batch_files)}")
    print(f"  Config/Doc files: {len(config_files)}")
    print(f"  Other files: {len(other_files)}")
    print()

    # Analyze each category
    python_analysis = analyze_python_files(python_files)
    batch_analysis = analyze_batch_files(batch_files)
    config_analysis = analyze_config_files(config_files)
    other_analysis = analyze_other_files(other_files)

    return {
        "python": python_analysis,
        "batch": batch_analysis,
        "config": config_analysis,
        "other": other_analysis,
    }


def analyze_python_files(python_files):
    """Detailed analysis of Python files"""

    print("PYTHON FILES INDIVIDUAL ANALYSIS:")
    print("=" * 80)

    analyses = []

    for file_path in python_files:
        print(f"\nANALYZING: {file_path.name}")
        print("-" * 60)

        # Get file stats
        stat = file_path.stat()
        size_kb = stat.st_size / 1024
        modified = datetime.fromtimestamp(stat.st_mtime)
        modified_str = modified.strftime("%Y-%m-%d %H:%M")

        print(f"Size: {size_kb:.1f}KB")
        print(f"Modified: {modified_str}")

        # Read and analyze content
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.split("\n")
            total_lines = len(lines)
            code_lines = len(
                [l for l in lines if l.strip() and not l.strip().startswith("#")]
            )

            print(f"Lines: {total_lines} total, {code_lines} code")

            # Look for imports and purpose
            imports = [
                l.strip()
                for l in lines[:20]
                if l.strip().startswith(("import ", "from "))
            ]

            # Find docstring or comments that indicate purpose
            purpose = "Unknown"
            for i, line in enumerate(lines[:15]):
                if '"""' in line or "'''" in line:
                    # Look for purpose in docstring
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if (
                            lines[j].strip()
                            and '"""' not in lines[j]
                            and "'''" not in lines[j]
                        ):
                            purpose = lines[j].strip()
                            break
                    break
                elif line.strip().startswith("#") and len(line.strip()) > 5:
                    purpose = line.strip()[1:].strip()
                    break

            print(f"Purpose: {purpose}")
            print("Key imports:")
            for imp in imports[:3]:
                print(f"  {imp}")

        except Exception as e:
            content = ""
            print(f"Could not read file: {e}")

        # Categorize and assess
        assessment = categorize_python_file(file_path.name, content, size_kb, modified)
        analyses.append(assessment)

        print(f"Category: {assessment['category']}")
        print(f"Status: {assessment['status']}")
        print(f"Recommendation: {assessment['recommendation']}")
        if assessment["notes"]:
            print(f"Notes: {assessment['notes']}")

    return analyses


def categorize_python_file(filename, content, size_kb, modified):
    """Categorize and assess individual Python file"""

    filename_lower = filename.lower()

    assessment = {
        "filename": filename,
        "size_kb": size_kb,
        "modified": modified,
        "category": "Unknown",
        "status": "Active",
        "recommendation": "Keep",
        "notes": "",
    }

    # Core system files
    if filename_lower in ["main.py", "launcher.py", "config.py"]:
        assessment["category"] = "CORE_SYSTEM"
        assessment["status"] = "Essential"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "Essential trading system component"

    # Strategy files
    elif "strateg" in filename_lower:
        assessment["category"] = "STRATEGY"
        assessment["status"] = "Active"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "Trading strategy configuration"

    # Dashboard and monitoring
    elif any(x in filename_lower for x in ["dashboard", "live_", "monitor", "status"]):
        assessment["category"] = "MONITORING"
        assessment["status"] = "Active"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "Live monitoring and dashboard"

    # P&L and reporting
    elif any(x in filename_lower for x in ["pnl", "report", "analysis"]):
        assessment["category"] = "REPORTING"
        assessment["status"] = "Active"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "P&L and reporting tools"

    # Emergency and protection
    elif any(x in filename_lower for x in ["emergency", "close", "force"]):
        assessment["category"] = "EMERGENCY"
        assessment["status"] = "Standby"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "Emergency trading controls"

    # Position management
    elif any(x in filename_lower for x in ["position", "order", "trade"]):
        assessment["category"] = "POSITION_MGMT"
        assessment["status"] = "Active"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "Position and order management"

    # Launch and utility
    elif any(x in filename_lower for x in ["launch", "start"]):
        assessment["category"] = "LAUNCHER"
        assessment["status"] = "Active"
        assessment["recommendation"] = "Keep"
        assessment["notes"] = "System launcher/starter"

    # Cleanup and maintenance
    elif any(x in filename_lower for x in ["cleanup", "phase", "final", "assessment"]):
        assessment["category"] = "MAINTENANCE"
        assessment["status"] = "Temporary"
        assessment["recommendation"] = "Archive"
        assessment["notes"] = "Cleanup/maintenance script - can be archived"

    else:
        assessment["category"] = "UTILITY"
        assessment["status"] = "Review"
        assessment["recommendation"] = "Review"
        assessment["notes"] = "Utility script - needs individual assessment"

    return assessment


def analyze_batch_files(batch_files):
    """Analyze batch files"""

    print("\nBATCH FILES ANALYSIS:")
    print("=" * 40)

    for file_path in batch_files:
        size_kb = file_path.stat().st_size / 1024
        modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%m-%d")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Look for what the batch file does
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            purpose = "Unknown"

            if lines:
                first_line = lines[0]
                if first_line.startswith("@echo") or first_line.startswith("echo"):
                    purpose = (
                        first_line.replace("@echo off", "").replace("echo", "").strip()
                    )
                elif "python" in first_line.lower():
                    purpose = f"Runs {first_line.split()[-1] if first_line.split() else 'Python script'}"
                else:
                    purpose = first_line

        except:
            purpose = "Could not read"

        print(f"  {file_path.name:<30} {size_kb:>5.1f}KB  {modified}  {purpose}")

    return batch_files


def analyze_config_files(config_files):
    """Analyze configuration and documentation files"""

    print("\nCONFIG/DOCUMENTATION FILES:")
    print("=" * 40)

    for file_path in config_files:
        size_kb = file_path.stat().st_size / 1024
        modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%m-%d")

        file_type = "Unknown"
        if file_path.suffix == ".md":
            file_type = "Documentation"
        elif file_path.suffix == ".txt":
            file_type = "Text/Requirements"
        elif file_path.suffix == ".ini":
            file_type = "Configuration"
        elif file_path.suffix == ".json":
            file_type = "JSON Config"

        print(f"  {file_path.name:<30} {size_kb:>5.1f}KB  {modified}  {file_type}")

    return config_files


def analyze_other_files(other_files):
    """Analyze other file types"""

    if other_files:
        print("\nOTHER FILES:")
        print("=" * 40)

        for file_path in other_files:
            size_kb = file_path.stat().st_size / 1024
            modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
                "%m-%d"
            )
            print(
                f"  {file_path.name:<30} {size_kb:>5.1f}KB  {modified}  {file_path.suffix}"
            )

    return other_files


def create_optimization_recommendations(analysis_results):
    """Create final optimization recommendations"""

    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    python_analyses = analysis_results["python"]

    # Group by recommendation
    keep_files = [a for a in python_analyses if a["recommendation"] == "Keep"]
    archive_candidates = [
        a for a in python_analyses if a["recommendation"] == "Archive"
    ]
    review_needed = [a for a in python_analyses if a["recommendation"] == "Review"]

    print(f"\nKEEP (Essential/Active): {len(keep_files)} files")
    for a in keep_files:
        print(f"  ✅ {a['filename']:<30} [{a['category']}] - {a['notes']}")

    if archive_candidates:
        print(f"\nARCHIVE (Temporary/Maintenance): {len(archive_candidates)} files")
        for a in archive_candidates:
            print(f"  📦 {a['filename']:<30} [{a['category']}] - {a['notes']}")

    if review_needed:
        print(f"\nREVIEW NEEDED: {len(review_needed)} files")
        for a in review_needed:
            print(f"  🔍 {a['filename']:<30} [{a['category']}] - {a['notes']}")

    # Final recommendations
    print(f"\nFINAL ROOT DIRECTORY ASSESSMENT:")
    print("-" * 40)
    print(
        f"✅ Essential files: {len([a for a in python_analyses if a['status'] == 'Essential'])}"
    )
    print(
        f"🟢 Active files: {len([a for a in python_analyses if a['status'] == 'Active'])}"
    )
    print(
        f"🟡 Standby files: {len([a for a in python_analyses if a['status'] == 'Standby'])}"
    )
    print(
        f"🔍 Review files: {len([a for a in python_analyses if a['status'] == 'Review'])}"
    )
    print(
        f"📦 Temporary files: {len([a for a in python_analyses if a['status'] == 'Temporary'])}"
    )

    if archive_candidates:
        print(f"\nRECOMMENDED FINAL ACTION:")
        print(
            f"Archive {len(archive_candidates)} maintenance/cleanup files to complete organization"
        )
    else:
        print(f"\nROOT DIRECTORY STATUS: WELL ORGANIZED")
        print("All files appear to have ongoing purpose and value")

    return archive_candidates


if __name__ == "__main__":
    try:
        print("Starting comprehensive root directory review...")
        print()

        analysis_results = analyze_root_directory()
        archive_candidates = create_optimization_recommendations(analysis_results)

        print("\n" + "=" * 80)
        print("ROOT DIRECTORY REVIEW COMPLETE")
        print("=" * 80)
        print(f"✅ All files analyzed and categorized")
        print(f"✅ Optimization recommendations provided")

        if archive_candidates:
            print(f"✅ {len(archive_candidates)} files identified for final cleanup")
        else:
            print(f"✅ Root directory is well organized")

        print(f"✅ Review complete and ready for action")

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
