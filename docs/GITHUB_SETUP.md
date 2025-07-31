# GitHub Setup Guide for HelpMeSign

This guide will help you set up the HelpMeSign project on GitHub with proper Git configuration and CI/CD workflows.

## 🚀 Quick Setup

### 1. Initialize Git Repository

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: HelpMeSign Python GUI application

- Complete Python GUI application with tkinter
- Comprehensive test suite with unit, integration, and mock tests
- Build scripts for macOS, Windows, and Linux
- Professional project structure with proper packaging
- CI/CD workflows with GitHub Actions
- Resource management system
- Fixed 1024x1024 window size
- Custom application icon"

# Add GitHub remote
git remote add origin https://github.com/vksvicky/HelpMeSign.git

# Create and switch to development branch
git checkout -b development

# Push to GitHub
git push -u origin development
```

### 2. Create Main Branch

```bash
# Create main branch from development
git checkout -b main

# Push main branch
git push -u origin main
```

### 3. Set Up Branch Protection

1. Go to your GitHub repository: https://github.com/vksvicky/HelpMeSign
2. Navigate to **Settings** → **Branches**
3. Add branch protection rule for `main`:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators
   - ✅ Restrict pushes that create files that are larger than 100 MB

## 📋 Repository Structure

```
HelpMeSign/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml             # Continuous Integration
│       └── release.yml        # Build and Release
├── scripts/                   # Build scripts
│   ├── build_macos_app.py    # macOS app builder
│   ├── build_windows_exe.py  # Windows executable builder
│   ├── build_linux_app.py    # Linux executable builder
│   └── build_all.py          # Universal builder
├── src/                      # Source code
│   └── helpmesign/
├── tests/                    # Test suite
├── resources/                # Application resources
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── run_app.py              # Application runner
├── run_tests.py            # Test runner
└── build.py                # Convenience build script
```

## 🔧 GitHub Actions Workflows

### CI/CD Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `development` branches
- Pull requests to `main` branch

**Jobs:**
1. **Test** - Runs tests on multiple Python versions (3.8-3.12)
2. **Lint** - Code quality checks (flake8, black, isort, mypy)
3. **Build** - Tests application startup on multiple platforms
4. **Security** - Security scanning (bandit, safety)

### Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Release published
- Manual workflow dispatch

**Jobs:**
1. **Build macOS** - Creates `.app` bundle and `.dmg`
2. **Build Windows** - Creates `.exe` and installer
3. **Build Linux** - Creates executable and `.tar.gz`
4. **Create Release** - Packages all artifacts

## 🎯 Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature: description"

# Push feature branch
git push -u origin feature/new-feature
```

### 2. Pull Request Process

1. Create Pull Request from `feature/new-feature` to `development`
2. Ensure all CI checks pass
3. Get code review approval
4. Merge to `development`

### 3. Release Process

1. Create Pull Request from `development` to `main`
2. Ensure all tests pass
3. Merge to `main`
4. Create GitHub Release with version tag
5. GitHub Actions will automatically build executables

## 📦 Release Management

### Creating a Release

1. **Update version** in `src/helpmesign/__init__.py`
2. **Create release branch:**
   ```bash
   git checkout -b release/v1.0.0
   git push -u origin release/v1.0.0
   ```
3. **Create Pull Request** to `main`
4. **Merge** after review
5. **Create GitHub Release:**
   - Go to **Releases** → **Create a new release**
   - Tag: `v1.0.0`
   - Title: `HelpMeSign v1.0.0`
   - Description: Release notes
   - **Publish release**

### Release Assets

GitHub Actions will automatically create:
- `HelpMeSign.app` (macOS)
- `HelpMeSign.exe` (Windows)
- `HelpMeSign` (Linux)
- Installers and packages

## 🔒 Security

### Repository Security

1. **Enable security features:**
   - Go to **Settings** → **Security**
   - Enable **Dependency graph**
   - Enable **Dependabot alerts**
   - Enable **Code scanning**

2. **Set up Dependabot:**
   - Go to **Security** → **Dependabot**
   - Enable for Python dependencies

### Code Quality

The CI pipeline includes:
- **Flake8** - Style guide enforcement
- **Black** - Code formatting
- **isort** - Import sorting
- **mypy** - Type checking
- **Bandit** - Security linting

## 📊 Monitoring

### GitHub Insights

Monitor your repository with:
- **Pulse** - Recent activity
- **Contributors** - Development activity
- **Traffic** - Clone and view statistics
- **Commits** - Development frequency

### CI/CD Metrics

Track:
- Build success rates
- Test coverage
- Security scan results
- Release frequency

## 🚨 Troubleshooting

### Common Issues

1. **CI/CD Failures:**
   - Check workflow logs in **Actions** tab
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Build Failures:**
   - Check platform-specific requirements
   - Verify resource files exist
   - Check PyInstaller/py2app compatibility

3. **Test Failures:**
   - Run tests locally: `python3 run_tests.py --verbose`
   - Check for missing dependencies
   - Verify test environment setup

### Getting Help

1. **Check existing issues** on GitHub
2. **Create new issue** with detailed description
3. **Include logs** and error messages
4. **Specify environment** (OS, Python version)

## 🎉 Success Checklist

- [ ] Repository created on GitHub
- [ ] Initial code pushed to `development` branch
- [ ] `main` branch created and protected
- [ ] CI/CD workflows working
- [ ] First release created
- [ ] Documentation updated
- [ ] Security features enabled
- [ ] Development workflow established

## 📞 Support

For questions or issues:
1. Check the [README.md](README.md) for project documentation
2. Review [scripts/README.md](scripts/README.md) for build instructions
3. Create an issue on GitHub for bugs or feature requests
4. Check CI/CD logs for build or test failures

---

**Happy coding! 🚀** 