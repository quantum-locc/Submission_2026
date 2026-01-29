# GitHub Repository Setup Instructions
==========================================

Follow these steps to create your anonymous GitHub repository for Nature Physics submission.

## Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Repository name: `quantum-locc-experiment`
4. Description: "Code and data for Nature Physics submission on LOCC irreversibility"
5. Select "Public" (reviewers need access)
6. Do NOT initialize with README (we have one)
7. Click "Create repository"

## Step 2: Upload Files

### Option A: Using Git Command Line

```bash
cd /path/to/github_repo

# Initialize git
git init
git add .
git commit -m "Initial commit - Nature Physics submission"

# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/quantum-locc-experiment.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Web Interface

1. Go to your new repository
2. Click "uploading an existing file"
3. Drag and drop all files from `github_repo/` folder
4. Commit directly to main

## Step 3: Verify Repository

Check that your repo contains:
```
✓ README.md
✓ LICENSE
✓ requirements.txt
✓ src/experiment.py
✓ src/analysis.py
✓ data/hardware_results_20260129_113343.json
```

## Step 4: Test the Code (Optional)

On a fresh machine:
```bash
git clone https://github.com/YOUR_USERNAME/quantum-locc-experiment.git
cd quantum-locc-experiment
pip install -r requirements.txt
python src/analysis.py data/hardware_results_20260129_113343.json
```

Should generate figures and print statistics.

## Step 5: Get Repository URL

Your repository URL will be:
```
https://github.com/YOUR_USERNAME/quantum-locc-experiment
```

## Step 6: Update Manuscript

In your Nature Physics submission, Data Availability section:

```latex
\section*{Data Availability}

All experimental data, including raw measurement counts, are publicly 
available at https://github.com/YOUR_USERNAME/quantum-locc-experiment. 
Upon acceptance, data will be permanently archived on Zenodo with an 
assigned DOI.

\section*{Code Availability}

Complete analysis code and circuit implementations are publicly available 
at https://github.com/YOUR_USERNAME/quantum-locc-experiment. The repository 
includes step-by-step instructions for reproducing all analyses and figures.
```

## Maintaining Anonymity (If Needed)

If you want to keep authorship anonymous during review:

### Option 1: Anonymous GitHub Account
- Create new GitHub account: `anonymous-researcher-2026`
- Upload code there
- Reveal identity after acceptance

### Option 2: Use OSF.io
- Go to https://osf.io
- Create anonymous project
- Upload files
- Get anonymous view link
- Share link with reviewers

**Note:** Nature Physics cares more about open science than strict anonymity.
Your name is in the cover letter anyway. Public GitHub is fine.

## After Acceptance

1. Archive on Zenodo:
   - Go to https://zenodo.org
   - Connect GitHub repository
   - Create release
   - Get DOI

2. Update manuscript with DOI:
   ```
   Data available at: https://doi.org/10.5281/zenodo.XXXXX
   ```

## Troubleshooting

**Problem:** "Permission denied"
**Solution:** Configure git credentials
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Problem:** Files too large
**Solution:** Data file is only ~500KB, should be fine. GitHub limit is 100MB.

**Problem:** Don't want to use Git
**Solution:** Use GitHub web interface to upload files directly

## Questions?

- GitHub Help: https://docs.github.com
- Git Tutorial: https://git-scm.com/doc

---

Repository ready for Nature Physics submission!
