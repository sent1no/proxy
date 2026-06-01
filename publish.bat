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
:: Check Remote existence
git remote get-url origin >nul 2>&1
if !errorlevel! neq 0 (
    echo [PROMPT] Set up GitHub Repository.
    set /p "raw_url=Paste your GitHub URL (SSH or HTTPS): "
    
    :: Convert SSH to HTTPS if it starts with git@
    set "final_url=!raw_url!"
    if "!raw_url:~0,3!"=="git" (
        set "final_url=!raw_url:git@github.com:=https://github.com/!"
        :: Replace colon after user/org if still present in some formats
        set "final_url=!final_url::=/!"
    )
    
    echo [INFO] Configuring destination: !final_url!
    git remote add origin !final_url!
)

:: Push
echo [INFO] Pushing to GitHub...
echo [TIP] If browser window opens, please authorize there.
git push -u origin main
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Push failed. Let's try resetting the URL.
    git remote remove origin
    goto push_process
)

echo [SUCCESS] Everything is on GitHub!
pause
