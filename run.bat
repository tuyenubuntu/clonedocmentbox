@echo off
chcp 65001 >nul
echo Dang khoi dong ung dung Scribd Downloader...

:: Tim duong dan Conda
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
    echo [LOI] Khong tim thay Cong cu Conda!
    pause
    exit /b 1
)

call %CONDA_ACTIVATE%

:: Kich hoat moi truong QT_env
call conda activate QT_env

:: Chay ung dung
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [THONG BAO] Ung dung dung lai voi ma loi.
    pause
)