@echo off
color 0A
echo ============================================================
echo   UPLOADING REAL TRAINED MODEL TO GITHUB / RENDER
echo ============================================================
echo.

:: Stage the model file explicitly
git add -f models\test_model_v1.pkl
git add .gitignore
git add api\main.py

:: Commit the model
git commit -m "Upload real trained ML model for Render"

:: Push the model to GitHub
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo Wait, trying 'master' branch instead...
    git push origin master
)

echo.
echo ============================================================
echo   SUCCESS! The real ML model has been uploaded.
echo   Render will now redeploy automatically!
echo ============================================================
pause
