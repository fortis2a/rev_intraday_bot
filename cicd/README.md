# 🚀 CI/CD System - Quick Reference

This folder contains all the CI/CD (Continuous Integration/Continuous Deployment) components for the trading bot.

## 📁 **File Organization**

### **Core Configuration Files**
- **`pyproject.toml`** - Code formatting, testing, and coverage configuration
- **`.flake8`** - Code linting rules and exclusions
- **`CICD_SETUP.md`** - Detailed GitHub repository setup instructions

### **Scripts & Tools**
- **`run_ci_checks.py`** - Run all CI checks locally before pushing
- **`deployment_dashboard.py`** - Monitor deployment status and pipeline health
- **`CI_CD_README.md`** - Complete user guide and troubleshooting

### **GitHub Workflows** (in `.github/workflows/`)
- **`ci-cd.yml`** - Main CI/CD pipeline with staging and production deployments
- **`dev.yml`** - Development workflow for feature branches

## 🚀 **Quick Start Commands**

### Test Before Pushing
```bash
# Run all CI checks locally
python cicd/run_ci_checks.py
```

### Monitor Deployments
```bash
# Check deployment status
python cicd/deployment_dashboard.py
```

### Auto-format Code
```bash
# Install tools (one-time setup)
pip install black isort flake8

# Format your code
black .
isort .
```

## 📋 **Setup Checklist**

### ✅ **GitHub Configuration Required**
1. **Add API Keys** to repository secrets:
   - `ALPACA_PAPER_API_KEY` / `ALPACA_PAPER_SECRET_KEY`
   - `ALPACA_LIVE_API_KEY` / `ALPACA_LIVE_SECRET_KEY`

2. **Create Environments**:
   - `staging` - Paper trading (auto-deploy)
   - `production` - Live trading (manual approval required)

3. **Set Branch Protection** on `main` branch

### 📖 **Detailed Instructions**
See `CICD_SETUP.md` for complete step-by-step setup guide.

## 🎯 **Workflow Triggers**

| Branch/Action | What Happens |
|---------------|--------------|
| `feature/*` push | Quick validation + auto-formatting |
| `develop` push | Full CI + auto-deploy to paper trading |
| `main` push | Full CI + manual production deployment option |
| Pull Request | Full CI validation |

## 🔒 **Safety Features**

- **Environment Isolation** - Paper vs live trading separation
- **Manual Approval** - Required for all production deployments  
- **Security Scanning** - Automatic vulnerability detection
- **Code Quality** - Formatting, linting, type checking
- **Emergency Rollback** - Automatic backup tagging

## 🆘 **Emergency Procedures**

### Stop All Trading
```bash
./emergency_close_all.py
./scripts/emergency_cleanup.ps1
```

### Rollback Deployment
```bash
git tag -l "production-*"  # View available backups
git checkout production-YYYYMMDD-HHMMSS
# Then trigger manual deployment from GitHub Actions
```

---

**⚠️ IMPORTANT:** Always test in staging (paper trading) before production! Live trading carries financial risk.

For help: Check `CI_CD_README.md` or the detailed setup guide in `CICD_SETUP.md`
