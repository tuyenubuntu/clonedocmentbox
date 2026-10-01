@echo off
chcp 65001 >nul
echo ========================================================
echo   DANG THIET LAP MOI TRUONG CONDA (QT_env) VA CAI DAT
echo ========================================================

:: Tim va kich hoat file khoi dong cua Conda
set CONDA_ACTIVATE=""
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set CONDA_ACTIVATE="%USERPROFILE%\miniconda3\Scripts\activate.bat"
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set CONDA_ACTIVATE="%USERPROFILE%\anaconda3\Scripts\activate.bat"
) else if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    set CONDA_ACTIVATE="C:\ProgramData\miniconda3\Scripts\activate.bat"
) else if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    set CONDA_ACTIVATE="C:\ProgramData\anaconda3\Scripts\activate.bat"
)

if %CONDA_ACTIVATE%=="" (
    echo [LOI] Khong tim thay duong dan activate.bat cua Conda!
    echo Vui long kiem tra lai duong dan cai dat Miniconda/Anaconda.
    pause
    exit /b 1
)

call %CONDA_ACTIVATE%

:: Kiem tra xem moi truong QT_env da ton tai chua
call conda info --envs | findstr /I "QT_env" >nul
if %errorlevel% neq 0 (
    echo [INFO] Dang tao moi truong Conda 'QT_env' voi Python 3.11...
    call conda create -n QT_env python=3.11 -y
) else (
    echo [INFO] Moi truong 'QT_env' da ton tai.
)

:: Kich hoat moi truong QT_env va cai dat thu vien
echo [INFO] Dang kich hoat moi truong QT_env...
call conda activate QT_env

echo [INFO] Dang cai dat cac thu vien can thiet tu requirements.txt...
pip install -r requirements.txt

echo.
echo ========================================================
echo   CAI DAT HOAN TAT! BAN CO THE DUNG FILE run.bat DE CHAY
echo ========================================================
pause