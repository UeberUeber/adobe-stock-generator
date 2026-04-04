@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================
::  ImageFX Auto Pipeline
::
::  Usage: run-pipeline.bat [image_count] [delay_ms] [timestamp] [final]
::    image_count : 생성할 이미지 수 (기본: 50)
::    delay_ms    : 요청 간 딜레이 (기본: 5000)
::    timestamp   : 공유 타임스탬프 (없으면 자동 생성)
::    final       : "final" 이면 업스케일+CSV+리포트 실행
:: ============================================================

set "IMAGEFX_DIR=%~dp0"
set "STOCK_DIR=%IMAGEFX_DIR%.."
set "COUNT=%~1"
set "DELAY=%~2"
set "TIMESTAMP=%~3"
set "IS_FINAL=%~4"

if "%COUNT%"=="" set "COUNT=50"
if "%DELAY%"=="" set "DELAY=5000"

:: Timestamp (외부에서 안 넘어오면 자동 생성)
if "%TIMESTAMP%"=="" (
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
    set "TIMESTAMP=!DT:~0,4!-!DT:~4,2!-!DT:~6,2!_!DT:~8,2!-!DT:~10,2!-!DT:~12,2!"
    :: 단독 실행이면 final 기본값
    if "%IS_FINAL%"=="" set "IS_FINAL=final"
)

echo ============================================================
echo   ImageFX Auto Pipeline
echo   %date% %time%
echo   Count: %COUNT% / Delay: %DELAY%ms
echo   Timestamp: %TIMESTAMP%
echo   Mode: %IS_FINAL%
echo ============================================================

:: ─── Step 1: Generate prompts via Claude CLI ───
echo.
echo [Step 1] Generating %COUNT% prompts via Claude CLI...
cd /d "%IMAGEFX_DIR%"

call node src/generate-prompts.js --count %COUNT%
if errorlevel 1 (
    echo [FAIL] Prompt generation failed
    call node src/report.js "%TIMESTAMP%" --error "Prompt generation failed. Check claude --version and network connection."
    exit /b 1
)

:: ─── Step 2: Generate images via ImageFX API ───
echo.
echo [Step 2] Generating images via ImageFX API...

call node src/generate.js --timestamp "%TIMESTAMP%" --delay %DELAY%
if errorlevel 1 (
    echo [FAIL] Image generation failed
    call node src/report.js "%TIMESTAMP%" --error "ImageFX image generation failed. Possible cookie expiration or rate limit."
    exit /b 1
)

:: ─── Step 3: Caption + Metadata enrichment (30-35 keywords) ───
echo.
echo [Step 3] Enriching metadata (captions + 30-35 keywords)...
cd /d "%IMAGEFX_DIR%"

call node src/enrich-metadata.js "%TIMESTAMP%"
if errorlevel 1 (
    echo [WARN] Metadata enrichment failed, continuing with basic metadata...
)

:: ─── Step 4: Crop + Upscale (매 회차 실행) ───
echo.
echo [Step 4] Processing images (crop + upscale)...
cd /d "%STOCK_DIR%"

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)
call python generation_pipeline.py "%TIMESTAMP%"
if errorlevel 1 (
    echo [FAIL] Image processing failed
    cd /d "%IMAGEFX_DIR%"
    call node src/report.js "%TIMESTAMP%" --error "generation_pipeline.py crop/upscale failed. Check GPU memory and torch installation."
    exit /b 1
)

:: ─── 중간 회차면 여기서 종료 ───
if /i not "%IS_FINAL%"=="final" (
    echo.
    echo [OK] Round complete (images saved to %TIMESTAMP%). Waiting for next round...
    exit /b 0
)

:: ─── Step 5: Generate CSV (final only) ───
echo.
echo [Step 5] Generating submission CSV...

call python generate_submission_csv.py "%TIMESTAMP%"
if errorlevel 1 (
    echo [FAIL] CSV generation failed
    cd /d "%IMAGEFX_DIR%"
    call node src/report.js "%TIMESTAMP%" --error "CSV generation failed. Check JSON metadata files."
    exit /b 1
)

:: ─── Step 6: Report + Open folder (final only) ───
echo.
echo [OK] Pipeline complete!
cd /d "%IMAGEFX_DIR%"
call node src/report.js "%TIMESTAMP%"
start "" explorer.exe "%STOCK_DIR%\generations\%TIMESTAMP%\upscaled"

endlocal
