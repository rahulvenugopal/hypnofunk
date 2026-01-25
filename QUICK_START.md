# Quick Reference: GitHub & PyPI Setup

## 🚀 Quick Start Commands

### 1. GitHub Setup (5 minutes)

```powershell
# Navigate to package
cd c:\Users\Rahul\Desktop\pipipaara

# Initialize and push to GitHub
git init
git add .
git commit -m "Initial commit: hypnofunk v0.1.0"
git remote add origin https://github.com/rahulvenugopal/hypnofunk.git
git branch -M main
git push -u origin main
```

**Manual Step**: Create repository at <https://github.com/new>

- Name: `hypnofunk`
- Public repository
- Don't initialize with README

### 2. PyPI Upload (10 minutes)

```powershell
# Install tools
python -m pip install --upgrade build twine

# Build package
python -m build

# Test on TestPyPI (optional but recommended)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

**Manual Steps**:

1. Create PyPI account: <https://pypi.org/account/register/>
2. Create API token: <https://pypi.org/manage/account/token/>
3. When uploading, use:
   - Username: `__token__`
   - Password: Your API token

---

## 📋 Pre-Upload Checklist

- [x] Package structure verified
- [x] All tests pass
- [x] Documentation complete
- [x] GitHub URLs updated
- [ ] GitHub repository created
- [ ] PyPI account created
- [ ] Package built successfully
- [ ] Uploaded to TestPyPI (optional)
- [ ] Uploaded to PyPI

---

## 📚 Detailed Guides

- **GitHub Setup**: See `GITHUB_SETUP.md`
- **PyPI Upload**: See `PYPI_UPLOAD.md`
- **Package Verification**: See `verification_report.md`

---

## 🔗 Important Links

- **GitHub Profile**: <https://github.com/rahulvenugopal>
- **Repository** (after creation): <https://github.com/rahulvenugopal/hypnofunk>
- **PyPI** (after upload): <https://pypi.org/project/hypnofunk/>
- **TestPyPI**: <https://test.pypi.org/project/hypnofunk/>

---

## ⚡ One-Line Installation (After PyPI Upload)

```bash
pip install hypnofunk
```

---

## 🆘 Need Help?

1. **GitHub Issues**: Check `GITHUB_SETUP.md` for troubleshooting
2. **PyPI Issues**: Check `PYPI_UPLOAD.md` for common errors
3. **Package Issues**: Run `python test_package.py`

---

## 📝 Next Steps After Upload

1. ✅ Add badges to README.md
2. ✅ Create GitHub release (v0.1.0)
3. ✅ Share on social media / research communities
4. ✅ Add to your CV/portfolio
5. ✅ Monitor PyPI downloads and GitHub stars
