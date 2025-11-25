# Maya's Veggie Run - Web Deployment Guide

This guide will help you deploy Maya's Veggie Run to the web using GitHub Pages.

## Prerequisites

- Python 3.8 or higher (your current version is 3.7.4, you'll need to upgrade)
- A GitHub account
- Git installed on your computer

## Step 1: Upgrade Python (Required)

Your current Python version is 3.7.4, but `pygbag` requires Python 3.8+.

**Download Python 3.11+:**
- Visit: https://www.python.org/downloads/
- Download and install the latest version
- Make sure to check "Add Python to PATH" during installation

**Verify installation:**
```bash
python --version
```
(Should show 3.8 or higher)

## Step 2: Install pygbag

Once you have Python 3.8+, install pygbag:

```bash
pip install pygbag
```

## Step 3: Build the Web Version

In your game directory, run:

```bash
pygbag main.py
```

This will:
- Create a `build/web` folder with your game
- Start a local web server
- Open your game in a browser to test it

**Test your game locally** to make sure everything works!

## Step 4: Set Up GitHub Repository

### Option A: Using GitHub Desktop (Easier)

1. Download GitHub Desktop: https://desktop.github.com/
2. Open GitHub Desktop and sign in
3. Click "Add" → "Create New Repository"
   - Name: `mayas-veggie-run` (or any name you like)
   - Local Path: Select your `MayasAdventure` folder
   - Click "Create Repository"
4. Click "Publish repository" to push it to GitHub

### Option B: Using Git Command Line

1. Initialize git repository:
```bash
cd c:\Users\unrea\Downloads\MayasAdventure
git init
git add .
git commit -m "Initial commit: Maya's Veggie Run"
```

2. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name it `mayas-veggie-run`
   - Don't initialize with README
   - Click "Create repository"

3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/mayas-veggie-run.git
git branch -M main
git push -u origin main
```

## Step 5: Deploy to GitHub Pages

### Method 1: Manual Deployment (Easiest)

1. Build the web version:
```bash
pygbag --build main.py
```

2. This creates a `build/web` folder. Copy its contents to a new `docs` folder:
```bash
mkdir docs
xcopy build\web docs /E /I
```

3. Commit and push:
```bash
git add docs
git commit -m "Add web build"
git push
```

4. Enable GitHub Pages:
   - Go to your repository on GitHub
   - Click "Settings" → "Pages"
   - Under "Source", select "main" branch and "/docs" folder
   - Click "Save"

5. Your game will be live at:
   `https://YOUR_USERNAME.github.io/mayas-veggie-run/`

### Method 2: GitHub Actions (Automated)

Create `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install pygbag
        run: pip install pygbag

      - name: Build game
        run: pygbag --build main.py

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build/web
```

Then:
1. Commit and push this file
2. Enable GitHub Pages (Settings → Pages → Source: gh-pages branch)
3. Every time you push changes, it will automatically rebuild and deploy!

## Step 6: Share Your Game!

Once deployed, share your game URL:
`https://YOUR_USERNAME.github.io/mayas-veggie-run/`

## Troubleshooting

### Game won't load
- Check browser console (F12) for errors
- Make sure all asset paths use forward slashes `/`
- Verify all files are in the `build/web` folder

### Assets missing
- Make sure the `assets` folder is in the same directory as `main.py`
- Rebuild with `pygbag --build main.py`

### Music not playing
- MP3 support varies in browsers
- Consider converting to OGG format for better compatibility

## File Structure

Your repository should look like this:
```
MayasAdventure/
├── main.py              # Web-compatible game file (with asyncio)
├── Maya.py              # Original desktop version
├── assets/
│   ├── images/
│   └── sounds/
├── docs/                # GitHub Pages deployment (if using manual method)
│   └── (web build files)
├── .gitignore
└── WEB_DEPLOYMENT.md    # This file
```

## Notes

- `main.py` is your web version (with asyncio support)
- `Maya.py` is your original desktop version
- Both work the same way, but `main.py` is optimized for web browsers
- The web version runs in the browser using WebAssembly
- No installation needed - anyone can play it in their browser!

## Next Steps

1. Customize your game's look on GitHub (add a nice README.md)
2. Add screenshots to your repository
3. Share the link with friends and family!

Good luck! 🎮
