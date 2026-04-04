@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================
::  ImageFX Self-Scheduling Runner
::
::  02:00~07:00 사이에 총 6회 수행. 간격 30~70분 랜덤.
::  6회 모두 같은 타임스탬프 폴더에 저장.
::  마지막 회차(1회 남음)에만 업스케일+CSV 실행.
::  6회 완료 후 -> 다음날 02:00 + 랜덤(0~30분)에 재시작.
::
::  Usage: run-scheduled.bat [remaining_runs] [timestamp]
::    remaining_runs : 남은 실행 횟수 (기본: 6)
::    timestamp      : 공유 타임스탬프 (첫 실행 시 자동 생성)
:: ============================================================

set "SCRIPT_PATH=%~f0"
set "PIPELINE_PATH=%~dp0run-pipeline.bat"
set "LOG_PATH=%~dp0logs\scheduler.log"
set "TS_FILE=%~dp0logs\current_timestamp.txt"
set "REMAINING=%~1"
set "TIMESTAMP=%~2"

if "%REMAINING%"=="" set "REMAINING=6"

:: Ensure logs dir exists
if not exist "%~dp0logs" mkdir "%~dp0logs"

:: ─── 타임스탬프 관리 ───
if "%TIMESTAMP%"=="" (
    if "%REMAINING%"=="6" (
        :: 첫 실행: 새 타임스탬프 생성
        for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
        set "TIMESTAMP=!DT:~0,4!-!DT:~4,2!-!DT:~6,2!_!DT:~8,2!-!DT:~10,2!-!DT:~12,2!"
    ) else (
        :: 중간 실행: 파일에서 읽기
        if exist "!TS_FILE!" (
            set /p TIMESTAMP=<"!TS_FILE!"
        ) else (
            :: 파일 없으면 새로 생성 (비정상 상황)
            for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
            set "TIMESTAMP=!DT:~0,4!-!DT:~4,2!-!DT:~6,2!_!DT:~8,2!-!DT:~10,2!-!DT:~12,2!"
            echo [WARN] Timestamp file missing, created new: !TIMESTAMP! >> "%LOG_PATH%"
        )
    )
)

:: 타임스탬프 파일에 저장
echo !TIMESTAMP!> "!TS_FILE!"

set /a RUN_NUM=7 - %REMAINING%
echo [%date% %time%] === Run %RUN_NUM%/6 (remaining: %REMAINING%) / TS: %TIMESTAMP% === >> "%LOG_PATH%"
echo [%date% %time%] Starting pipeline (run %RUN_NUM%/6, remaining: %REMAINING%)

:: ─── 파이프라인 실행 ───
set "FINAL_FLAG="
if %REMAINING% LEQ 1 set "FINAL_FLAG=final"

call "%PIPELINE_PATH%" 50 5000 "%TIMESTAMP%" %FINAL_FLAG%
set "PIPE_RESULT=!errorlevel!"

if !PIPE_RESULT! EQU 0 (
    echo [%date% %time%] Pipeline run %RUN_NUM%/6 succeeded >> "%LOG_PATH%"
) else (
    echo [%date% %time%] Pipeline run %RUN_NUM%/6 FAILED (exit code: !PIPE_RESULT!) >> "%LOG_PATH%"
)

:: ─── 다음 스케줄 등록 (파이프라인 성공/실패 무관하게 항상 실행) ───
set /a NEXT_REMAINING=%REMAINING% - 1

if %NEXT_REMAINING% LEQ 0 (
    :: 6회 완료. 타임스탬프 파일 정리
    if exist "!TS_FILE!" del "!TS_FILE!"

    :: 다음날 02:00 + 랜덤 0~30분
    set /a RAND_MIN=%RANDOM% %% 30
    set "NEXT_HOUR=02"
    if !RAND_MIN! LSS 10 (
        set "NEXT_MIN=0!RAND_MIN!"
    ) else (
        set "NEXT_MIN=!RAND_MIN!"
    )

    :: 내일 날짜 계산
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
    set /a TODAY_DAY=1%DT:~6,2% - 100
    set /a TOMORROW_DAY=!TODAY_DAY! + 1
    if !TOMORROW_DAY! LSS 10 (
        set "DAY_STR=0!TOMORROW_DAY!"
    ) else (
        set "DAY_STR=!TOMORROW_DAY!"
    )
    set "TOMORROW=!DT:~0,4!/!DT:~4,2!/!DAY_STR!"

    schtasks /Create /TN "ImageFX_Pipeline" /TR "\"%SCRIPT_PATH%\" 6" /SC ONCE /SD !TOMORROW! /ST !NEXT_HOUR!:!NEXT_MIN! /F >nul 2>&1

    echo [%date% %time%] All 6 runs done. Next cycle: !TOMORROW! !NEXT_HOUR!:!NEXT_MIN! >> "%LOG_PATH%"
    echo [OK] All 6 runs done. Next cycle: !TOMORROW! !NEXT_HOUR!:!NEXT_MIN!
) else (
    :: 다음 실행: 30~70분 후
    set /a DELAY_MIN=%RANDOM% %% 41 + 30

    for /f "tokens=1-2 delims=:" %%a in ("%time: =0%") do (
        set /a CUR_HOUR=1%%a - 100
        set /a CUR_MIN=1%%b - 100
    )
    set /a NEXT_TOTAL_MIN=!CUR_HOUR! * 60 + !CUR_MIN! + !DELAY_MIN!
    set /a NEXT_HOUR=!NEXT_TOTAL_MIN! / 60
    set /a NEXT_MIN=!NEXT_TOTAL_MIN! %% 60

    :: 07:00 넘으면 내일로 연기
    if !NEXT_HOUR! GEQ 7 (
        set /a RAND_MIN=%RANDOM% %% 30
        set "NEXT_HOUR=02"
        if !RAND_MIN! LSS 10 (
            set "NEXT_MIN=0!RAND_MIN!"
        ) else (
            set "NEXT_MIN=!RAND_MIN!"
        )
        set "NEXT_REMAINING=6"

        :: 타임스탬프 파일 정리 (미완료 사이클이지만 내일 새로 시작)
        if exist "!TS_FILE!" del "!TS_FILE!"

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

        echo [%date% %time%] Past 07:00, deferred to tomorrow: !TOMORROW! !NEXT_HOUR!:!NEXT_MIN! (incomplete cycle, will restart fresh) >> "%LOG_PATH%"
    ) else (
        if !NEXT_HOUR! LSS 10 set "NEXT_HOUR=0!NEXT_HOUR!"
        if !NEXT_MIN! LSS 10 set "NEXT_MIN=0!NEXT_MIN!"

        schtasks /Create /TN "ImageFX_Pipeline" /TR "\"%SCRIPT_PATH%\" !NEXT_REMAINING! \"%TIMESTAMP%\"" /SC ONCE /ST !NEXT_HOUR!:!NEXT_MIN! /F >nul 2>&1

        echo [%date% %time%] Next run at !NEXT_HOUR!:!NEXT_MIN! (%DELAY_MIN%min later), %NEXT_REMAINING% remaining >> "%LOG_PATH%"
        echo [OK] Next run scheduled: !NEXT_HOUR!:!NEXT_MIN! (%DELAY_MIN%min later), %NEXT_REMAINING% runs left
    )
)

endlocal
