@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================
::  ImageFX Self-Scheduling Runner
::
::  1회 실행 후 다음 실행을 랜덤 시간에 자동 재등록.
::  02:00~07:00 사이에 총 6회 수행. 간격 30~70분 랜덤.
::  6회 완료 후 -> 다음날 02:00 + 랜덤(0~30분)에 재시작.
::
::  Usage: run-scheduled.bat [remaining_runs]
::    remaining_runs : 남은 실행 횟수 (기본: 6)
:: ============================================================

set "SCRIPT_PATH=%~f0"
set "PIPELINE_PATH=%~dp0run-pipeline.bat"
set "LOG_PATH=%~dp0logs\scheduler.log"
set "REMAINING=%~1"

if "%REMAINING%"=="" set "REMAINING=6"

:: Ensure logs dir exists
if not exist "%~dp0logs" mkdir "%~dp0logs"

echo [%date% %time%] === Run %REMAINING% remaining === >> "%LOG_PATH%"

:: ─── Run the pipeline ───
echo [%date% %time%] Starting pipeline (run %REMAINING% of 6)
echo [%date% %time%] Pipeline started >> "%LOG_PATH%"

call "%PIPELINE_PATH%" 50 5000

echo [%date% %time%] Pipeline finished >> "%LOG_PATH%"

:: ─── Schedule next run ───
set /a NEXT_REMAINING=%REMAINING% - 1

if %NEXT_REMAINING% LEQ 0 (
    :: All 6 runs done. Schedule tomorrow at 02:00 + random 0~30min
    set /a RAND_MIN=%RANDOM% %% 30
    set "NEXT_HOUR=02"
    if !RAND_MIN! LSS 10 (
        set "NEXT_MIN=0!RAND_MIN!"
    ) else (
        set "NEXT_MIN=!RAND_MIN!"
    )

    :: Get tomorrow's date
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
    set /a TODAY_DAY=1%DT:~6,2% - 100
    set /a TOMORROW_DAY=%TODAY_DAY% + 1
    if %TOMORROW_DAY% LSS 10 (
        set "DAY_STR=0%TOMORROW_DAY%"
    ) else (
        set "DAY_STR=%TOMORROW_DAY%"
    )
    set "TOMORROW=%DT:~0,4%/%DT:~4,2%/%DAY_STR%"

    schtasks /Create /TN "ImageFX_Pipeline" /TR "\"%SCRIPT_PATH%\" 6" /SC ONCE /SD %TOMORROW% /ST !NEXT_HOUR!:!NEXT_MIN! /F >nul 2>&1

    echo [%date% %time%] All 6 runs done. Next cycle: %TOMORROW% !NEXT_HOUR!:!NEXT_MIN! >> "%LOG_PATH%"
    echo [OK] All 6 runs done. Next cycle: %TOMORROW% !NEXT_HOUR!:!NEXT_MIN!
) else (
    :: Schedule next run in 30~70 minutes
    set /a DELAY_MIN=%RANDOM% %% 41 + 30

    :: Calculate next time
    for /f "tokens=1-2 delims=:" %%a in ("%time: =0%") do (
        set /a CUR_HOUR=1%%a - 100
        set /a CUR_MIN=1%%b - 100
    )
    set /a NEXT_TOTAL_MIN=!CUR_HOUR! * 60 + !CUR_MIN! + !DELAY_MIN!
    set /a NEXT_HOUR=!NEXT_TOTAL_MIN! / 60
    set /a NEXT_MIN=!NEXT_TOTAL_MIN! %% 60

    :: Don't schedule past 07:00
    if !NEXT_HOUR! GEQ 7 (
        :: Too late, schedule remaining for tomorrow
        set /a RAND_MIN=%RANDOM% %% 30
        set "NEXT_HOUR=02"
        if !RAND_MIN! LSS 10 (
            set "NEXT_MIN=0!RAND_MIN!"
        ) else (
            set "NEXT_MIN=!RAND_MIN!"
        )
        set "NEXT_REMAINING=6"

        for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
        set /a TODAY_DAY=1%DT:~6,2% - 100
        set /a TOMORROW_DAY=!TODAY_DAY! + 1
        if !TOMORROW_DAY! LSS 10 (
            set "DAY_STR=0!TOMORROW_DAY!"
        ) else (
            set "DAY_STR=!TOMORROW_DAY!"
        )
        set "TOMORROW=!DT:~0,4!/!DT:~4,2!/!DAY_STR!"

        schtasks /Create /TN "ImageFX_Pipeline" /TR "\"%SCRIPT_PATH%\" !NEXT_REMAINING!" /SC ONCE /SD !TOMORROW! /ST !NEXT_HOUR!:!NEXT_MIN! /F >nul 2>&1

        echo [%date% %time%] Past 07:00, deferred to tomorrow: !TOMORROW! !NEXT_HOUR!:!NEXT_MIN! >> "%LOG_PATH%"
    ) else (
        :: Format time
        if !NEXT_HOUR! LSS 10 set "NEXT_HOUR=0!NEXT_HOUR!"
        if !NEXT_MIN! LSS 10 set "NEXT_MIN=0!NEXT_MIN!"

        schtasks /Create /TN "ImageFX_Pipeline" /TR "\"%SCRIPT_PATH%\" !NEXT_REMAINING!" /SC ONCE /ST !NEXT_HOUR!:!NEXT_MIN! /F >nul 2>&1

        echo [%date% %time%] Next run at !NEXT_HOUR!:!NEXT_MIN! (%DELAY_MIN%min later), %NEXT_REMAINING% remaining >> "%LOG_PATH%"
        echo [OK] Next run scheduled: !NEXT_HOUR!:!NEXT_MIN! (%DELAY_MIN%min later), %NEXT_REMAINING% runs left
    )
)

endlocal
