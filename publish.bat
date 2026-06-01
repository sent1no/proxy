@echo off
setlocal enabledelayedexpansion
cd /d %%~dp0

git --version >nul 2>&1 || (echo [ERROR] Git is not installed! & pause & exit /b 1)
if not exist ".git" (git init & git checkout -b main)
git add .
git diff --cached --quiet || (
    set /p msg="Commit message [Default: chore: publish]: "
    if "!msg!"=="" set msg=chore: publish
    git commit -m "!msg!"
)
git remote get-url origin >nul 2>&1 || git remote add origin https://github.com/%USERNAME%/information-security-practice.git
echo [INFO] Pushing to origin/main...
git push -u origin main || (
    echo [ERROR] Push failed. Create the repo first.
    pause
    exit /b 1
)
echo [SUCCESS] Published.
pause
