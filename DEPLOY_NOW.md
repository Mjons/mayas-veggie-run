# Deploy Maya's Veggie Run to GitHub Pages - Quick Guide

Everything is ready! Just follow these 4 steps:

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `mayas-veggie-run` (or any name you want)
3. Make it **Public** (required for free GitHub Pages)
4. **DO NOT** check "Add a README file"
5. Click "Create repository"

## Step 2: Push Your Code

Copy these commands from the GitHub page (they'll look similar to this):

```bash
git remote add origin https://github.com/YOUR_USERNAME/mayas-veggie-run.git
git branch -M main
git push -u origin main
```

Run them in PowerShell in your game folder.

**Example:**
```powershell
cd c:\Users\unrea\Downloads\MayasAdventure
git remote add origin https://github.com/YOUR_USERNAME/mayas-veggie-run.git
git branch -M main
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under **Source**, select:
   - Source: **GitHub Actions**
5. The page will auto-save

## Step 4: Wait for Deployment

1. Go to the **Actions** tab in your repository
2. You'll see "Build and Deploy Maya's Veggie Run" running
3. Wait 2-3 minutes for it to complete (green checkmark)
4. Your game will be live at:

   **https://YOUR_USERNAME.github.io/mayas-veggie-run/**

## That's It!

The game is now deployed and playable in any web browser!

### Future Updates

Whenever you want to update the game:
1. Make your changes to the code
2. Run:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. GitHub will automatically rebuild and redeploy!

## Troubleshooting

**If Actions fails:**
- Check the Actions tab for error messages
- Make sure all asset files are in the `assets` folder
- Verify `main.py` exists

**If the game page is blank:**
- Wait a few more minutes
- Clear your browser cache
- Check browser console (F12) for errors

**Need help?**
- Check the Actions log for detailed error messages
- Make sure the repository is Public
- Verify GitHub Pages is set to "GitHub Actions" source

---

Your game is ready to share with the world! 🎮
