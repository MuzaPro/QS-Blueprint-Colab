@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  OVERNIGHT RENDER - NOV 25
:: ================================================================
::  Renders, one after the other:
::    1. SH_02 v04, frames 1-250
::    2. SH_15 v22, the frames that are still missing (50-850)
::
::  It only starts the two shots' own scripts. All settings (frames,
::  samples, cooldown, output folder) stay in those scripts and .blends:
::    SH_02\render_SH_02_v04.bat
::    SH_15\Sh_15_v22_render_script.bat
::
::  Frames that already exist are skipped, so you can close this window
::  and double-click again to continue.
::  If a frame fails, the shot is retried after 2 minutes, up to 3 times;
::  then the next shot starts. Results: overnight-render-nov25_log.txt
:: ================================================================

set "NO_PAUSE=1"
set /a MAX_TRIES=3
set /a RETRY_WAIT=120
set "MASTER_LOG=%~dp0overnight-render-nov25_log.txt"
set /a FAILED=0

echo.>> "%MASTER_LOG%"
echo ==== STARTED %date% %time% ====>> "%MASTER_LOG%"

call :run_shot "SH_02 v04" "%~dp0SH_02\render_SH_02_v04.bat"
call :run_shot "SH_15 v22" "%~dp0SH_15\Sh_15_v22_render_script.bat"

echo ==== FINISHED %date% %time%  (shots not finished: !FAILED!) ====>> "%MASTER_LOG%"
echo.
echo  ================================================================
echo   OVERNIGHT RENDER FINISHED   %date%  %time%
echo   Shots not finished: !FAILED!
echo   Details: %MASTER_LOG%
echo  ================================================================
title Overnight render finished - shots not finished: !FAILED!
if not defined MASTER_NO_PAUSE pause
exit /b !FAILED!


:run_shot
set /a TRY=0
:try_again
set /a TRY+=1
echo.
echo  ================================================================
echo   %~1  -  attempt !TRY! of %MAX_TRIES%   %date%  %time%
echo  ================================================================
echo [%date% %time%]  %~1: attempt !TRY! started>> "%MASTER_LOG%"
call "%~2"
if not errorlevel 1 (
    echo [!date! !time!]  %~1: COMPLETE>> "%MASTER_LOG%"
    exit /b 0
)
echo [%date% %time%]  %~1: stopped with an error on attempt !TRY!>> "%MASTER_LOG%"
if !TRY! lss %MAX_TRIES% (
    echo   Retrying in %RETRY_WAIT% seconds...
    timeout /t %RETRY_WAIT% /nobreak >nul
    goto try_again
)
echo [%date% %time%]  %~1: GIVEN UP after %MAX_TRIES% attempts>> "%MASTER_LOG%"
set /a FAILED+=1
exit /b 1
