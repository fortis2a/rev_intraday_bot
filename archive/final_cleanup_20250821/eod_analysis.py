#!/usr/bin/env python3
"""
End-of-Day Analysis Script
Wrapper for the comprehensive market close report generator
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the comprehensive market close report generator
from market_close_report import MarketCloseReportGenerator


def main():
    """Main EOD analysis function"""
    print("🚀 Starting End-of-Day Analysis...")
    
    try:
        # Use the comprehensive market close report generator
        generator = MarketCloseReportGenerator()
        report_path = generator.generate_report()
        
        print(f"✅ EOD Analysis Complete!")
        print(f"📄 Report saved: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ EOD Analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)