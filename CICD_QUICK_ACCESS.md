# 🚀 CI/CD System Quick Access

The complete CI/CD (Continuous Integration/Continuous Deployment) system has been organized in the **`cicd/`** folder for easy access.

## 📁 **Quick Navigation**

### **🛠️ Daily Use Tools**
- **`cicd/run_ci_checks.bat`** - Double-click to test code before pushing *(Windows)*
- **`cicd/deployment_dashboard.bat`** - Double-click to check deployment status *(Windows)*
- **`cicd/run_ci_checks.py`** - Run CI checks *(Cross-platform)*
- **`cicd/deployment_dashboard.py`** - Monitor deployments *(Cross-platform)*

### **📖 Documentation**
- **`cicd/README.md`** - Complete CI/CD reference and quick commands
- **`cicd/CICD_SETUP.md`** - Detailed GitHub repository setup guide
- **`cicd/CI_CD_README.md`** - Full user guide with troubleshooting

### **⚙️ Configuration Files**
- **`cicd/pyproject.toml`** - Code formatting and testing configuration
- **`cicd/.flake8`** - Code linting rules

### **🔄 GitHub Workflows**
- **`.github/workflows/ci-cd.yml`** - Main CI/CD pipeline
- **`.github/workflows/dev.yml`** - Development workflow

## 🚀 **Quick Start**

### **Test Your Code Before Pushing**
```bash
# Option 1: Double-click (Windows)
# cicd/run_ci_checks.bat

# Option 2: Command line
python cicd/run_ci_checks.py
```

### **Check Deployment Status**
```bash
# Option 1: Double-click (Windows)  
# cicd/deployment_dashboard.bat

# Option 2: Command line
python cicd/deployment_dashboard.py
```

### **Get Complete Setup Instructions**
```bash
# Read the setup guide
code cicd/CICD_SETUP.md
```

## 🔒 **Safety First**
- **Paper Trading** - All changes deploy to paper trading first
- **Manual Approval** - Production requires your explicit approval
- **Emergency Stops** - Emergency scripts remain in root for quick access

---

**📁 Everything CI/CD related is now organized in the `cicd/` folder for easy access!**
