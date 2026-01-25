# PyPI Upload Guide for hypnofunk

## Prerequisites

Before uploading to PyPI, ensure:

- ✅ GitHub repository is created and pushed
- ✅ All tests pass
- ✅ Package version is correct in `hypnofunk/__init__.py`
- ✅ CHANGELOG.md is up to date

## Step 1: Create PyPI Account

1. Go to <https://pypi.org/account/register/>
2. Create an account
3. Verify your email address
4. **IMPORTANT**: Enable Two-Factor Authentication (2FA) for security

## Step 2: Create TestPyPI Account (Recommended)

Test your upload on TestPyPI first:

1. Go to <https://test.pypi.org/account/register/>
2. Create a separate account
3. Verify email

## Step 3: Install Build Tools

```powershell
# Install build and twine
python -m pip install --upgrade build twine
```

## Step 4: Build Distribution Packages

```powershell
# Navigate to package directory
cd c:\Users\Rahul\Desktop\pipipaara

# Clean previous builds (if any)
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# Build distribution packages
python -m build
```

This creates:

- `dist/hypnofunk-0.1.0.tar.gz` (source distribution)
- `dist/hypnofunk-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 5: Test Upload to TestPyPI (Recommended)

```powershell
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:

- Username: Your TestPyPI username
- Password: Your TestPyPI password (or API token)

### Test Installation from TestPyPI

```powershell
# Create a test environment
python -m venv test_env
test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ hypnofunk

# Test the package
python -c "from hypnofunk import hypnoman; print('Success!')"

# Deactivate and remove test environment
deactivate
Remove-Item -Recurse -Force test_env
```

## Step 6: Upload to PyPI (Production)

Once testing is successful:

```powershell
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for:

- Username: Your PyPI username (or `__token__` if using API token)
- Password: Your PyPI password or API token

### Using API Tokens (Recommended)

1. Go to <https://pypi.org/manage/account/token/>
2. Create a new API token
3. Scope: "Entire account" or specific to "hypnofunk" project
4. Copy the token (starts with `pypi-`)
5. When uploading, use:
   - Username: `__token__`
   - Password: Your API token

## Step 7: Verify Upload

1. Visit <https://pypi.org/project/hypnofunk/>
2. Check that:
   - ✅ README is displayed correctly
   - ✅ Version is correct
   - ✅ Links work
   - ✅ Classifiers are correct

## Step 8: Test Installation from PyPI

```powershell
# Create fresh environment
python -m venv verify_env
verify_env\Scripts\activate

# Install from PyPI
pip install hypnofunk

# Test basic functionality
python -c "from hypnofunk import hypnoman, analyze_transitions; print('Package installed successfully!')"

# Deactivate
deactivate
Remove-Item -Recurse -Force verify_env
```

## Step 9: Update README Badge (Optional)

Add PyPI badge to README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/hypnofunk.svg)](https://badge.fury.io/py/hypnofunk)
[![Downloads](https://pepy.tech/badge/hypnofunk)](https://pepy.tech/project/hypnofunk)
```

## Troubleshooting

### Error: "File already exists"

- You cannot re-upload the same version
- Increment version in `hypnofunk/__init__.py`
- Update CHANGELOG.md
- Rebuild and upload

### Error: "Invalid distribution"

- Check that `setup.py` and `pyproject.toml` are correct
- Ensure `README.md` exists
- Verify all required files are included

### Error: "Authentication failed"

- Check username/password
- If using API token, username must be `__token__`
- Ensure 2FA is configured correctly

## Future Updates

When releasing new versions:

1. Update version in `hypnofunk/__init__.py`
2. Update `CHANGELOG.md`
3. Commit changes to GitHub
4. Create GitHub release with tag (e.g., `v0.2.0`)
5. Build new distribution: `python -m build`
6. Upload to PyPI: `python -m twine upload dist/*`

## Quick Reference Commands

```powershell
# Complete upload process
cd c:\Users\Rahul\Desktop\pipipaara
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
python -m build
python -m twine upload dist/*
```

## Security Best Practices

1. ✅ Use API tokens instead of passwords
2. ✅ Enable 2FA on PyPI account
3. ✅ Never commit API tokens to git
4. ✅ Use project-scoped tokens when possible
5. ✅ Regularly rotate API tokens

---

## Installation Instructions for Users

After successful upload, users can install with:

```bash
# Basic installation
pip install hypnofunk

# Full installation with optional dependencies
pip install hypnofunk[full]
```

## Support

- 📝 Documentation: <https://github.com/rahulvenugopal/hypnofunk#readme>
- 🐛 Issues: <https://github.com/rahulvenugopal/hypnofunk/issues>
- 📦 PyPI: <https://pypi.org/project/hypnofunk/>
