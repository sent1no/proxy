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

:: Init if needed
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

:: Check Remote
git remote get-url origin >nul 2>&1
if !errorlevel! neq 0 (
    echo [PROMPT] Remote 'origin' not found.
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

echo [SUCCESS] Done!
pause
