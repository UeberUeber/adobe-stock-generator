@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================
::  ImageFX Auto Pipeline (6 Steps)
::  Windows Scheduler로 호출되는 메인 배치 파일
::
::  Usage: run-pipeline.bat [image_count] [delay_ms]
::    image_count : 생성할 이미지 수 (기본: 50)
::    delay_ms    : 요청 간 딜레이 (기본: 5000)
:: ============================================================

set "IMAGEFX_DIR=%~dp0"
set "STOCK_DIR=%IMAGEFX_DIR%..\adobe-stock-generator"
set "COUNT=%~1"
set "DELAY=%~2"

if "%COUNT%"=="" set "COUNT=50"
if "%DELAY%"=="" set "DELAY=5000"

:: Timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
set "TIMESTAMP=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%_%DT:~8,2%-%DT:~10,2%-%DT:~12,2%"

echo ============================================================
echo   ImageFX Auto Pipeline
echo   %date% %time%
echo   Count: %COUNT% / Delay: %DELAY%ms
echo ============================================================

:: ─── Step 1/6: Generate prompts via Claude CLI ───
echo.
echo [Step 1/6] Generating %COUNT% prompts via Claude CLI...
cd /d "%IMAGEFX_DIR%"

call node src/generate-prompts.js --count %COUNT%
if errorlevel 1 (
    echo [FAIL] Prompt generation failed
    call node src/report.js "%TIMESTAMP%" --error "Step 1 FAILED: Claude CLI prompt generation failed. Check claude --version and network connection."
    goto :end
)

:: ─── Step 2/6: Generate images via ImageFX API ───
echo.
echo [Step 2/6] Generating images via ImageFX API...

call node src/generate.js --timestamp "%TIMESTAMP%" --delay %DELAY%
if errorlevel 1 (
    echo [FAIL] Image generation failed
    call node src/report.js "%TIMESTAMP%" --error "Step 2 FAILED: ImageFX image generation failed. Possible cookie expiration or rate limit."
    goto :end
)

:: ─── Step 3/6: Caption + Metadata enrichment (30-35 keywords) ───
echo.
echo [Step 3/6] Enriching metadata (captions + 30-35 keywords)...
cd /d "%IMAGEFX_DIR%"

call node src/enrich-metadata.js "%TIMESTAMP%"
if errorlevel 1 (
    echo [WARN] Metadata enrichment failed, continuing with basic metadata...
)

:: ─── Step 4/6: Crop + Upscale ───
echo.
echo [Step 4/6] Processing images (crop + upscale)...
cd /d "%STOCK_DIR%"

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)
call python generation_pipeline.py "%TIMESTAMP%"
if errorlevel 1 (
    echo [FAIL] Image processing failed
    cd /d "%IMAGEFX_DIR%"
    call node src/report.js "%TIMESTAMP%" --error "Step 4 FAILED: generation_pipeline.py crop/upscale failed. Check GPU memory and torch installation."
    goto :end
)

:: ─── Step 5/6: Generate CSV ───
echo.
echo [Step 5/6] Generating submission CSV...

call python generate_submission_csv.py "%TIMESTAMP%"
if errorlevel 1 (
    echo [FAIL] CSV generation failed
    cd /d "%IMAGEFX_DIR%"
    call node src/report.js "%TIMESTAMP%" --error "Step 5 FAILED: CSV generation failed. Check JSON metadata files."
    goto :end
)

:: ─── Step 6/6: Report + Open folder ───
echo.
echo [OK] Pipeline complete!
cd /d "%IMAGEFX_DIR%"
call node src/report.js "%TIMESTAMP%"
start "" explorer.exe "%STOCK_DIR%\generations\%TIMESTAMP%\upscaled"
goto :done

:end
cd /d "%IMAGEFX_DIR%"
:: On failure, open the raw generations folder if it exists
if exist "%STOCK_DIR%\generations\%TIMESTAMP%" (
    start "" explorer.exe "%STOCK_DIR%\generations\%TIMESTAMP%"
)

:done
endlocal
