@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================
::  3 Rounds x 50 images = 150 total, single folder, CSV at end
:: ============================================================

set "IMAGEFX_DIR=%~dp0"
set "STOCK_DIR=%IMAGEFX_DIR%.."

:: Fixed timestamp for all 3 rounds (same folder)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
set "TIMESTAMP=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%_%DT:~8,2%-%DT:~10,2%-%DT:~12,2%"

echo ============================================================
echo   ImageFX Batch 150 (3 rounds x 50)
echo   Timestamp: %TIMESTAMP%
echo   %date% %time%
echo ============================================================

cd /d "%IMAGEFX_DIR%"

:: ─── Round 1/3 ───
echo.
echo [Round 1/3] Generating prompts...
call node src/generate-prompts.js --count 50
if errorlevel 1 goto :fail
echo [Round 1/3] Generating images...
call node src/generate.js --timestamp "%TIMESTAMP%" --delay 5000
if errorlevel 1 goto :fail
echo [Round 1/3] Enriching metadata...
call node src/enrich-metadata.js "%TIMESTAMP%"

echo.
set /a WAIT1=%RANDOM% %% 1800 + 2700
set /a WAIT1_MIN=!WAIT1! / 60
echo [Round 1/3 DONE] Waiting !WAIT1_MIN! min for Round 2...
timeout /t !WAIT1! /nobreak >nul

:: ─── Round 2/3 ───
echo.
echo [Round 2/3] Generating prompts...
call node src/generate-prompts.js --count 50
if errorlevel 1 goto :fail
echo [Round 2/3] Generating images...
call node src/generate.js --timestamp "%TIMESTAMP%" --delay 5000
if errorlevel 1 goto :fail
echo [Round 2/3] Enriching metadata...
call node src/enrich-metadata.js "%TIMESTAMP%"

echo.
set /a WAIT2=%RANDOM% %% 1800 + 2700
set /a WAIT2_MIN=!WAIT2! / 60
echo [Round 2/3 DONE] Waiting !WAIT2_MIN! min for Round 3...
timeout /t !WAIT2! /nobreak >nul

:: ─── Round 3/3 ───
echo.
echo [Round 3/3] Generating prompts...
call node src/generate-prompts.js --count 50
if errorlevel 1 goto :fail
echo [Round 3/3] Generating images...
call node src/generate.js --timestamp "%TIMESTAMP%" --delay 5000
if errorlevel 1 goto :fail
echo [Round 3/3] Enriching metadata...
call node src/enrich-metadata.js "%TIMESTAMP%"

:: ─── Upscale all 150 ───
echo.
echo [Step 4] Upscaling all 150 images...
cd /d "%STOCK_DIR%"
if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"
call python generation_pipeline.py "%TIMESTAMP%"
if errorlevel 1 goto :fail

:: ─── CSV for all 150 ───
echo.
echo [Step 5] Generating CSV for 150 images...
call python generate_submission_csv.py "%TIMESTAMP%"

:: ─── Report + Folder ───
echo.
echo [DONE] 150 images complete!
cd /d "%IMAGEFX_DIR%"
call node src/report.js "%TIMESTAMP%"
start "" explorer.exe "%STOCK_DIR%\generations\%TIMESTAMP%\upscaled"
goto :end

:fail
echo [FAIL] Pipeline failed at %date% %time%
cd /d "%IMAGEFX_DIR%"
call node src/report.js "%TIMESTAMP%" --error "Batch 150 failed. Check logs."
start "" explorer.exe "%STOCK_DIR%\generations\%TIMESTAMP%"

:end
endlocal
