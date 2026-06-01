@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

:: Check Git
git --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Git is not installed!
    pause
    exit /b
)

:: Init
if not exist ".git" (
    echo [INFO] Initializing Git...
    git init
    git checkout -b main
)

:: Add and Commit
echo [INFO] Adding files...
git add .
set /p msg="Enter commit message (default: 'feat: setup'): "
if "!msg!"=="" set msg=feat: setup
git commit -m "!msg!"

:push_process
:: Check Remote
git remote get-url origin >nul 2>&1
if !errorlevel! neq 0 (
    echo [PROMPT] Remote 'origin' not found.
    echo [TIP] Use HTTPS URL like: https://github.com/username/repo.git
    set /p "repo_url=Enter your GitHub Repository URL: "
    if not "!repo_url!"=="" (
        git remote add origin !repo_url!
    ) else (
        echo [ERROR] No URL provided.
        pause
        exit /b
    )
)

:: Push
echo [INFO] Pushing to GitHub...
git push -u origin main
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Push failed! 
    echo [TIP] If you used SSH (git@github.com...), try using HTTPS (https://github.com/...) instead.
    set /p "retry=Do you want to change the URL and try again? (y/n): "
    if /i "!retry!"=="y" (
        git remote remove origin
        goto push_process
    )
    pause
    exit /b
)

echo [SUCCESS] Everything is on GitHub!
pause
