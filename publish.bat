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
set /p msg="Commit message [Default: 'feat: project setup']: "
if "!msg!"=="" set msg=feat: project setup
git commit -m "!msg!"

:push_process
:: Check Remote
set "final_url=https://github.com/sent1no/proxy.git"
git remote get-url origin >nul 2>&1
if !errorlevel! neq 0 (
    echo [INFO] Configuring destination: !final_url!
    git remote add origin !final_url!
) else (
    :: Ensure origin matches the hardcoded URL
    git remote set-url origin !final_url!
    echo [INFO] Repository URL set to: !final_url!
)

:: Push
echo [INFO] Pushing to GitHub...
git push -u origin main
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Push failed. 
    echo [TIP] Make sure the repository EXISTS on GitHub (https://github.com/new).
    set /p "retry=Do you want to reset URL and try again? (y/n): "
    if /i "!retry!"=="y" (
        git remote remove origin
        goto push_process
    )
    pause
    exit /b
)

echo [SUCCESS] Everything is on GitHub!
pause
