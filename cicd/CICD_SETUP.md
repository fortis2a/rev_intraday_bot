# Environment Configuration for CI/CD

## GitHub Repository Settings Required

### 1. Repository Secrets
Navigate to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

```
# Paper Trading (Staging Environment)
ALPACA_PAPER_API_KEY=your_paper_api_key_here
ALPACA_PAPER_SECRET_KEY=your_paper_secret_key_here

# Live Trading (Production Environment) 
ALPACA_LIVE_API_KEY=your_live_api_key_here
ALPACA_LIVE_SECRET_KEY=your_live_secret_key_here
```

### 2. Environment Protection Rules
Navigate to Settings → Environments

#### Staging Environment
- **Name:** `staging`
- **Deployment branches:** `develop` branch only
- **Environment secrets:** Use paper trading keys
- **Required reviewers:** None (auto-deploy)

#### Production Environment  
- **Name:** `production`
- **Deployment branches:** `main` branch only
- **Environment secrets:** Use live trading keys
- **Required reviewers:** Add yourself as required reviewer
- **Wait timer:** 5 minutes (safety buffer)

### 3. Branch Protection Rules
Navigate to Settings → Branches

#### Main Branch Protection
- **Branch name pattern:** `main`
- **Require a pull request before merging** ✅
- **Require status checks to pass before merging** ✅
  - Required checks: `lint-and-format`, `test-suite`, `security-scan`
- **Require conversation resolution before merging** ✅
- **Restrict pushes to matching branches** ✅

#### Develop Branch Protection
- **Branch name pattern:** `develop`  
- **Require status checks to pass before merging** ✅
  - Required checks: `quick-validation`

## Workflow Triggers

### Automatic Triggers
- **Push to `main`:** Full CI/CD pipeline with production deployment option
- **Push to `develop`:** Full CI + auto-deploy to staging
- **Push to `feature/*`:** Quick validation + auto-formatting
- **Pull Request to `main`:** Full CI validation
- **Pull Request to `develop`:** Quick validation

### Manual Triggers
- **Production Deployment:** Use GitHub Actions "Run workflow" button
  - Select `main` branch
  - Choose `production` environment
  - Requires manual approval

## Safety Features

### 🔒 Security
- **Dependency scanning** with Safety
- **Code security** with Bandit  
- **Secret scanning** (GitHub built-in)
- **Environment isolation** between paper/live trading

### 🧪 Testing
- **Unit tests** run on every commit
- **Integration tests** for paper trading validation
- **Performance benchmarks** before production
- **Code coverage** tracking

### 🚀 Deployment Safety
- **Paper trading validation** before any live deployment
- **Manual approval required** for production
- **Automatic backups** with git tags
- **Rollback capability** built-in

## Usage Examples

### Feature Development
```bash
# Create feature branch
git checkout -b feature/new-strategy
# Make changes, push
git push origin feature/new-strategy
# Auto-formatting and quick validation runs
```

### Staging Deployment  
```bash
# Merge to develop branch
git checkout develop
git merge feature/new-strategy
git push origin develop
# Automatic deployment to paper trading
```

### Production Deployment
```bash
# Merge to main via PR
git checkout main
git merge develop
git push origin main
# Use GitHub UI to manually trigger production deployment
```

## Monitoring

### GitHub Actions Dashboard
- View all workflow runs
- Download logs and artifacts
- Monitor deployment status

### Deployment Summaries
- Automatic summary generation
- Environment status tracking
- Performance metrics

### Notifications
- Email notifications on deployment
- Slack integration (optional)
- Custom webhook support
