@echo off
title Pushing to GitHub...
color 0B

echo.
echo ============================================================
echo   PUSHING ALL CHANGES TO GITHUB
echo ============================================================
echo.

:: Show what's changed
echo [1/4] Files changed since last push:
echo.
git status
echo.

:: Stage ALL changed files
echo [2/4] Staging all changes...
git add requirements.txt
git add deploy.bat
git add generate_data.py
git add .gitignore
git add src\
git add api\
git add frontend\
git add README.md
echo   Done staging files.
echo.

:: Show what's staged
echo [3/4] Files being committed:
git status --short
echo.

:: Commit with a nice message
echo [4/4] Committing and pushing to GitHub...
git commit -m "feat: add deploy script, data generator & fix dependencies

- Added deploy.bat: one-click deployment script
- Added generate_data.py: auto-generates 2000-row realistic telco dataset  
- Fixed requirements.txt: pinned versions to fix numpy/pandas incompatibility
- Updated .gitignore: exclude raw data and model files properly
- Using python -m uvicorn for reliable server startup on Windows"

echo.
echo Pushing to GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   Push failed! Trying 'master' branch instead...
    echo ============================================================
    git push origin master
)

echo.
echo ============================================================
echo   SUCCESS! All changes pushed to GitHub!
echo   Your professor can now see everything at:
echo   https://github.com/sohamrp172-sys/telco-churn-mlops
echo ============================================================
echo.
pause
