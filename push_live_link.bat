@echo off
echo ============================================================
echo   PUSHING LIVE RENDER LINK TO GITHUB FOR PROFESSOR
echo ============================================================
echo.

git add README.md
git commit -m "docs: add live render url link for presentation"
git push

echo.
echo ============================================================
echo   SUCCESS! The live link is now at the top of your GitHub!
echo ============================================================
pause
