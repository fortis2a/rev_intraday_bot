#!/usr/bin/env python3
"""
🔧 Scalping Bot Setup Script
Helps configure the environment and validate the installation
"""

import os
import sys
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        print("📁 Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("✅ Created .env file")
        print("📝 Please edit .env file with your Alpaca API credentials")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ No .env.example template found")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "pandas", "numpy", "alpaca", "dotenv", "aiohttp", "requests", "dateutil"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "alpaca":
                __import__("alpaca")
            elif package == "dotenv":
                __import__("dotenv")
            elif package == "dateutil":
                __import__("dateutil")
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def validate_installation():
    """Validate the scalping bot installation"""
    print("🔍 Validating scalping bot installation...\n")
    
    # Check core files
    core_files = [
        "scalping_bot.py",
        "config.py",
        "core/scalping_engine.py",
        "core/data_manager.py",
        "core/order_manager.py",
        "core/risk_manager.py",
        "strategies/momentum_scalp.py",
        "strategies/mean_reversion.py",
        "strategies/vwap_bounce.py",
        "utils/logger.py"
    ]
    
    missing_files = []
    for file_path in core_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n📁 Creating directories...")
    create_directories()
    
    print("\n🔧 Setting up environment...")
    env_ok = setup_environment()
    
    print("\n" + "="*50)
    
    if len(missing_files) == 0 and deps_ok and env_ok:
        print("🎉 Installation validation successful!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your Alpaca API credentials")
        print("2. Test the bot: python scalping_bot.py --test AAPL")
        print("3. Run paper trading: python scalping_bot.py --dry-run")
        return True
    else:
        print("❌ Installation validation failed!")
        if len(missing_files) > 0:
            print(f"Missing files: {missing_files}")
        if not deps_ok:
            print("Missing dependencies - run: pip install -r requirements.txt")
        if not env_ok:
            print("Environment setup failed")
        return False

def main():
    """Main setup function"""
    print("⚡ Scalping Bot Setup")
    print("="*50)
    
    if validate_installation():
        print("\n🚀 Ready to start scalping!")
    else:
        print("\n🔧 Please fix the issues above and run setup again")
        sys.exit(1)

if __name__ == "__main__":
    main()
