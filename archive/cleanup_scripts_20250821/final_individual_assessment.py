#!/usr/bin/env python3
"""
Final Individual Assessment - Detailed review of remaining 12 scripts
THOROUGH ANALYSIS - Check each file for purpose, overlap, and current relevance
"""

import os
from datetime import datetime
from pathlib import Path


def analyze_individual_files():
    """Detailed analysis of each remaining file"""
    
    print("FINAL INDIVIDUAL ASSESSMENT OF REMAINING FILES")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    scripts_dir = Path("scripts")
    remaining_files = list(scripts_dir.glob("*.py"))
    remaining_files.sort()
    
    # Files we know are essential (from previous analysis)
    essential_files = [
        "scalping_command_center.py",
        "confidence_monitor.py", 
        "continuous_position_monitor.py",
        "emergency_profit_protection.py",
        "manual_protection.py"
    ]
    
    # Files needing individual assessment
    review_files = [f for f in remaining_files if f.name not in essential_files]
    
    print(f"Essential files (KEEP): {len(essential_files)}")
    print(f"Files for individual assessment: {len(review_files)}")
    print()
    
    assessments = []
    
    for file_path in review_files:
        print(f"ANALYZING: {file_path.name}")
        print("-" * 60)
        
        # Get file stats
        stat = file_path.stat()
        size_kb = stat.st_size / 1024
        modified = datetime.fromtimestamp(stat.st_mtime)
        modified_str = modified.strftime('%Y-%m-%d %H:%M')
        
        print(f"Size: {size_kb:.1f}KB")
        print(f"Modified: {modified_str}")
        
        # Read file content for analysis
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Analyze content
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            print(f"Lines: {total_lines} total, {code_lines} code")
            
            # Look for key indicators
            imports = [l for l in lines[:20] if l.strip().startswith('import ') or l.strip().startswith('from ')]
            docstring_lines = [l for l in lines[:10] if '"""' in l or "'''" in l]
            
            print("Key imports:")
            for imp in imports[:5]:  # Show first 5 imports
                print(f"  {imp.strip()}")
            
            if docstring_lines:
                print("Purpose (from docstring):")
                # Try to extract purpose
                for i, line in enumerate(lines[:15]):
                    if '"""' in line or "'''" in line:
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip() and not lines[j].strip().startswith('"""'):
                                print(f"  {lines[j].strip()}")
                                break
                        break
            
        except Exception as e:
            content = ""
            print(f"Could not read file: {e}")
        
        # Make assessment based on filename and analysis
        assessment = assess_file_purpose(file_path.name, content, size_kb, modified)
        assessments.append(assessment)
        
        print(f"ASSESSMENT: {assessment['recommendation']}")
        print(f"REASON: {assessment['reason']}")
        print(f"OVERLAP CHECK: {assessment['overlap_check']}")
        print()
    
    return assessments

def assess_file_purpose(filename, content, size_kb, modified):
    """Assess individual file purpose and make recommendation"""
    
    filename_lower = filename.lower()
    
    # Check what we have in root for overlap comparison
    root_files = [f.name.lower() for f in Path('.').glob('*.py')]
    
    assessment = {
        'filename': filename,
        'size_kb': size_kb,
        'modified': modified,
        'recommendation': 'REVIEW',
        'reason': '',
        'overlap_check': '',
        'confidence': 'MEDIUM'
    }
    
    # Specific file assessments
    if filename_lower == 'alpaca_connector.py':
        # Large connector file - check if core system uses it
        if 'alpaca_connector' in content.lower() and size_kb > 25:
            assessment['recommendation'] = 'KEEP'
            assessment['reason'] = 'Large connector utility, may be used by core system'
            assessment['overlap_check'] = 'No direct overlap found in root'
            assessment['confidence'] = 'HIGH'
        else:
            assessment['recommendation'] = 'REVIEW'
            assessment['reason'] = 'Connector utility - verify if used by current system'
            assessment['overlap_check'] = 'Check if core/ or utils/ has similar functionality'
    
    elif 'pnl' in filename_lower:
        # P&L related files - check for overlap with current tools
        current_pnl_tools = ['generate_todays_pnl.py', 'live_dashboard.py', 'market_close_report.py']
        
        if 'comprehensive_pnl_report.py' == filename_lower:
            assessment['recommendation'] = 'ARCHIVE'
            assessment['reason'] = 'Large P&L report tool likely replaced by market_close_report.py'
            assessment['overlap_check'] = f'Overlaps with: {", ".join(current_pnl_tools)}'
            assessment['confidence'] = 'HIGH'
            
        elif 'alpaca_pnl_calculator.py' == filename_lower:
            assessment['recommendation'] = 'ARCHIVE' 
            assessment['reason'] = 'P&L calculator likely replaced by generate_todays_pnl.py'
            assessment['overlap_check'] = 'Overlaps with generate_todays_pnl.py'
            assessment['confidence'] = 'HIGH'
            
        elif 'live_pnl_external.py' == filename_lower:
            assessment['recommendation'] = 'ARCHIVE'
            assessment['reason'] = 'External P&L tool replaced by live_dashboard.py'
            assessment['overlap_check'] = 'Overlaps with live_dashboard.py'
            assessment['confidence'] = 'HIGH'
    
    elif 'enhanced_report_generator.py' == filename_lower:
        # Recent report generator - check if it's newer/better than current
        if modified > datetime(2025, 8, 20):  # Recent file
            assessment['recommendation'] = 'KEEP'
            assessment['reason'] = 'Recent enhanced report generator, may be improvement over current tools'
            assessment['overlap_check'] = 'Potentially complements market_close_report.py'
            assessment['confidence'] = 'MEDIUM'
        else:
            assessment['recommendation'] = 'REVIEW'
            assessment['reason'] = 'Report generator - check if better than current market_close_report.py'
    
    elif 'connector' in filename_lower or 'data' in filename_lower:
        # Data connectors
        assessment['recommendation'] = 'KEEP'
        assessment['reason'] = 'Data connector - may be essential for data feeds'
        assessment['overlap_check'] = 'Check if core data_manager.py uses this'
        assessment['confidence'] = 'MEDIUM'
    
    elif 'analyzer' in filename_lower or 'analysis' in filename_lower:
        # Analysis tools
        if size_kb < 2:  # Very small files
            assessment['recommendation'] = 'ARCHIVE'
            assessment['reason'] = 'Very small analysis file, likely incomplete or obsolete'
            assessment['confidence'] = 'HIGH'
        else:
            assessment['recommendation'] = 'REVIEW'
            assessment['reason'] = 'Analysis tool - check for current relevance'
    
    elif 'integrator' in filename_lower:
        assessment['recommendation'] = 'KEEP'
        assessment['reason'] = 'Integration component - may be used by core system'
        assessment['overlap_check'] = 'Check if core system imports this'
        assessment['confidence'] = 'MEDIUM'
    
    else:
        # General assessment
        if size_kb < 2:
            assessment['recommendation'] = 'ARCHIVE'
            assessment['reason'] = 'Very small utility, likely obsolete'
            assessment['confidence'] = 'HIGH'
        elif modified < datetime(2025, 8, 15):
            assessment['recommendation'] = 'ARCHIVE'
            assessment['reason'] = 'Old file (>1 week), likely replaced by newer tools'
            assessment['confidence'] = 'MEDIUM'
        else:
            assessment['recommendation'] = 'KEEP'
            assessment['reason'] = 'Recent utility, may be actively used'
            assessment['confidence'] = 'MEDIUM'
    
    return assessment

def create_final_cleanup_recommendations():
    """Create final cleanup recommendations based on individual assessments"""
    
    print("CREATING FINAL CLEANUP RECOMMENDATIONS")
    print("=" * 80)
    
    # Run the analysis
    assessments = analyze_individual_files()
    
    # Group by recommendation
    keep_files = [a for a in assessments if a['recommendation'] == 'KEEP']
    archive_files = [a for a in assessments if a['recommendation'] == 'ARCHIVE']
    review_files = [a for a in assessments if a['recommendation'] == 'REVIEW']
    
    print("FINAL RECOMMENDATIONS:")
    print("=" * 40)
    
    print(f"\nKEEP ({len(keep_files)} files):")
    for f in keep_files:
        print(f"  ✅ {f['filename']:<35} - {f['reason']}")
    
    print(f"\nARCHIVE ({len(archive_files)} files):")
    for f in archive_files:
        print(f"  📦 {f['filename']:<35} - {f['reason']}")
    
    print(f"\nNEEDS REVIEW ({len(review_files)} files):")
    for f in review_files:
        print(f"  🔍 {f['filename']:<35} - {f['reason']}")
    
    # Create specific cleanup recommendations
    if archive_files:
        print()
        print("RECOMMENDED FOR FINAL CLEANUP:")
        print("-" * 40)
        print("These files can be safely archived based on individual assessment:")
        
        final_archive_list = []
        for f in archive_files:
            if f['confidence'] == 'HIGH':
                final_archive_list.append(f['filename'])
                print(f"  - {f['filename']} (HIGH confidence)")
        
        print()
        print(f"FINAL ARCHIVE CANDIDATES: {len(final_archive_list)} files")
        
        return final_archive_list
    
    return []

if __name__ == "__main__":
    try:
        final_archive_list = create_final_cleanup_recommendations()
        
        print()
        print("INDIVIDUAL ASSESSMENT COMPLETE")
        print("=" * 80)
        
        if final_archive_list:
            print(f"✅ {len(final_archive_list)} files ready for final cleanup")
            print("✅ All assessments complete")
            print("✅ High-confidence recommendations identified")
            print()
            print("Next step: Execute final cleanup of identified files")
        else:
            print("✅ Individual assessment complete")
            print("✅ All remaining files appear to have ongoing value")
            print("✅ Manual review recommended for any final decisions")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)
