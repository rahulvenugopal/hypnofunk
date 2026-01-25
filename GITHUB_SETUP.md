# GitHub Repository Setup Guide

## Step 1: Create GitHub Repository

1. Go to <https://github.com/rahulvenugopal>
2. Click the **"+"** button in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `hypnofunk`
   - **Description**: `A Python package for sleep analysis and hypnogram processing`
   - **Visibility**: Public (recommended for PyPI)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

## Step 2: Initialize Git and Push to GitHub

Open PowerShell in the package directory and run:

```powershell
# Navigate to package directory
cd c:\Users\Rahul\Desktop\pipipaara

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: hypnofunk v0.1.0 - Sleep analysis package"

# Add remote repository
git remote add origin https://github.com/rahulvenugopal/hypnofunk.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Verify GitHub Repository

After pushing, verify at: <https://github.com/rahulvenugopal/hypnofunk>

You should see:

- ✅ README.md displayed on the homepage
- ✅ All package files
- ✅ LICENSE file
- ✅ Proper folder structure

## Step 4: Add Repository Topics (Optional but Recommended)

On your GitHub repository page:

1. Click the ⚙️ gear icon next to "About"
2. Add topics: `sleep-analysis`, `python`, `polysomnography`, `hypnogram`, `sleep-stages`, `neuroscience`
3. Save changes

## Step 5: Create a Release (Optional)

1. Go to your repository on GitHub
2. Click on "Releases" (right sidebar)
3. Click "Create a new release"
4. Tag version: `v0.1.0`
5. Release title: `hypnofunk v0.1.0 - Initial Release`
6. Description: Copy from CHANGELOG.md
7. Click "Publish release"

---

## Next: PyPI Upload

After GitHub setup is complete, proceed to `PYPI_UPLOAD.md` for PyPI distribution instructions.
