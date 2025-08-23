# 🚀 Trading Bot CI/CD System

## Quick Start

### 1. Initial Setup
```bash
# Install CI/CD dependencies
pip install black flake8 isort mypy safety bandit pytest-benchmark

# Test local CI checks before pushing
python scripts/run_ci_checks.py
```

### 2. GitHub Setup
Follow the detailed guide in [`.github/CICD_SETUP.md`](.github/CICD_SETUP.md) to:
- Add API keys as repository secrets
- Configure environment protection rules
- Set up branch protection

### 3. Development Workflow

#### Feature Development
```bash
git checkout -b feature/my-new-feature
# Make changes...
python scripts/run_ci_checks.py  # Test locally first
git add .
git commit -m "Add new feature"
git push origin feature/my-new-feature
# Auto-formatting and validation runs
```

#### Staging Deployment (Paper Trading)
```bash
git checkout develop
git merge feature/my-new-feature
git push origin develop
# Automatic deployment to paper trading environment
```

#### Production Deployment (Live Trading)
```bash
# Create PR: develop → main
# After PR approval and merge:
# Use GitHub Actions UI to manually trigger production deployment
```

## 📊 Monitoring

### View Deployment Status
```bash
python scripts/deployment_dashboard.py
```

### Check CI/CD Pipeline
- Go to GitHub Actions tab in your repository
- View workflow runs and logs
- Monitor deployment status

## 🔒 Safety Features

### Automatic Checks
- ✅ Code formatting (Black)
- ✅ Import sorting (isort)  
- ✅ Code linting (flake8)
- ✅ Type checking (mypy)
- ✅ Security scanning (safety, bandit)
- ✅ Unit & integration tests
- ✅ Performance benchmarks

### Deployment Safety
- 🔒 **Staging environment** uses paper trading only
- 🔒 **Production environment** requires manual approval
- 🔒 **Environment isolation** prevents accidental live trading
- 🔒 **Automatic backups** before each deployment

## 🎯 Pipeline Triggers

| Trigger | Environment | Actions |
|---------|-------------|---------|
| Push to `feature/*` | Development | Quick validation + auto-format |
| Push to `develop` | Staging | Full CI + auto-deploy to paper trading |
| Push to `main` | Production | Full CI + manual production deployment |
| Pull Request | Validation | Full CI validation only |

## 🚨 Emergency Procedures

### Rollback Deployment
```bash
# View recent tags
git tag -l "production-*"

# Rollback to previous version
git checkout production-YYYYMMDD-HHMMSS
# Trigger manual deployment from this commit
```

### Stop All Trading
```bash
# Use existing emergency scripts
./emergency_close_all.py
./scripts/emergency_cleanup.ps1
```

## 📈 Performance Monitoring

The CI/CD system includes:
- Code coverage tracking
- Performance benchmarks
- Security vulnerability monitoring
- Deployment success/failure tracking

View metrics in:
- GitHub Actions dashboard
- Codecov (if configured)
- Local deployment dashboard

## 🛠️ Troubleshooting

### Common Issues

#### CI Checks Failing
```bash
# Run local checks to debug
python scripts/run_ci_checks.py

# Fix common issues
black .          # Auto-format code
isort .          # Fix import sorting
pytest tests/    # Run tests
```

#### Deployment Stuck
- Check GitHub Actions logs
- Verify API keys in repository secrets
- Check environment protection rules

#### Live Trading Accidentally Triggered
- Use emergency stop scripts immediately
- Check deployment dashboard
- Review GitHub Actions logs for trigger source

---

**⚠️ IMPORTANT:** Always test changes in staging (paper trading) before production deployment. Live trading carries financial risk!
