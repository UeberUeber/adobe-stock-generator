@echo off
chcp 65001 >nul 2>&1

:: ============================================================
::  ImageFX Scheduled Runner
::  Windows Task Scheduler에서 호출. 랜덤 딜레이 후 파이프라인 실행.
::  3~40분 랜덤 대기 -> run-pipeline.bat 50 5000
:: ============================================================

:: Random delay: 180~2400 seconds (3~40 minutes)
set /a DELAY_SEC=%RANDOM% %% 2220 + 180
set /a DELAY_MIN=%DELAY_SEC% / 60

echo [%date% %time%] Scheduled run starting. Random delay: %DELAY_MIN% min (%DELAY_SEC% sec)

:: Log the delay
echo [%date% %time%] Waiting %DELAY_MIN% minutes before pipeline start >> "%~dp0logs\scheduler.log"

timeout /t %DELAY_SEC% /nobreak >nul

echo [%date% %time%] Delay complete. Starting pipeline...
echo [%date% %time%] Pipeline started >> "%~dp0logs\scheduler.log"

:: Run the actual pipeline
call "%~dp0run-pipeline.bat" 50 5000

echo [%date% %time%] Pipeline finished >> "%~dp0logs\scheduler.log"
