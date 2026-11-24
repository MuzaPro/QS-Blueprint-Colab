@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  BLENDER SAFE RENDER  -  SH_01 quantum computers room
::  GPU cooldowns, hang watchdog, automatic retries and RESUME.
:: ================================================================
::
::  HOW TO USE
::  -------------------------------------------------------
::  Double-click this .bat (it sits next to the .blend).
::  If the render stops for any reason (crash, reboot, you close the
::  window), just double-click it again: it RESUMES where it left off.
::
::  HOW RESUME WORKS
::  -------------------------------------------------------
::  The output folder already holds playblast EXRs for every frame, so
::  "file exists" can't tell a finished frame from a playblast one.
::  Instead, every frame that renders successfully is written to
::     sh_01_04quantum_computers_room-AI-assisted_done_frames.txt
::  and frames listed there are skipped on the next run.
::  -> To re-render EVERYTHING from scratch, delete that txt file.
::  -> To re-render one frame, delete its number from that txt file.
::
::  WHEN A FRAME FAILS
::  -------------------------------------------------------
::  A frame that hangs, crashes, or finishes without writing its EXR
::  (e.g. GPU out of memory) is retried up to FRAME_RETRIES times.
::  If it still fails, it is logged and SKIPPED, and the render goes on.
::  Failed frames are listed at the end; run the .bat again to retry them.
::  If MAX_FAILS_IN_ROW frames fail back-to-back, the script stops
::  (something is badly wrong and it would just burn GPU time).
::
:: ================================================================


:: ================================================================
::  SETTINGS                                          <-- EDIT THIS
:: ================================================================

set "BLEND_NAME=sh_01_04quantum_computers_room-AI-assisted.blend"

set /a START_FRAME=1
set /a END_FRAME=200

:: Frames rendered before each GPU cooldown, and cooldown length.
set /a BATCH_SIZE=2
set /a COOLDOWN_SEC=60

:: A frame running longer than this is treated as frozen, killed and retried.
:: A normal SH_1 frame takes ~55-75 s at 150% / 256 samples. Keep this above the
:: .blend's Cycles time limit (180 s) plus sync + denoise time, or good frames get killed.
set /a FRAME_TIMEOUT_SEC=240
set /a FRAME_RETRIES=3
set /a MAX_FAILS_IN_ROW=3

:: Where the .blend saves its EXRs (Output Properties > Output path): a full path,
:: or relative to this folder. Used to check that each frame really wrote a new file.
:: Blender adds the 4-digit frame number + .exr, e.g. sh_01_QC_lab_polished0001.exr
set "OUTPUT_PREFIX=C:\Users\mrgav\Documents\GitHub\QS-Blueprint-Colab\08_renders\Final_draft\sh_01_QS_lab_polished\sh_01_QC_lab_polished"

set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


:: ================================================================
::  !! DO NOT EDIT ANYTHING BELOW THIS LINE !!
:: ================================================================

set "BLEND_FILE=%~dp0%BLEND_NAME%"
for %%F in ("%BLEND_NAME%") do set "BLEND_BASE=%%~nF"
set "LOG_FILE=%~dp0%BLEND_BASE%_render_log.txt"
set "DONE_FILE=%~dp0%BLEND_BASE%_done_frames.txt"
set "OUT_PREFIX_ABS=%~dp0%OUTPUT_PREFIX%"
if "%OUTPUT_PREFIX:~1,1%"==":" set "OUT_PREFIX_ABS=%OUTPUT_PREFIX%"


:: ================================================================
::  PRE-FLIGHT CHECKS
:: ================================================================

if not exist "%BLENDER_EXE%" (
    echo [INFO] Blender not found at configured path. Searching PATH...
    where blender >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('where blender') do (
            set "BLENDER_EXE=%%i"
            goto :blender_found
        )
    )
    echo.
    echo  [ERROR] Blender not found at: %BLENDER_EXE%
    echo  Open this .bat in Notepad and fix the BLENDER_EXE line.
    echo.
    pause
    exit /b 1
)

:blender_found
echo [OK] Blender:    %BLENDER_EXE%

if not exist "%BLEND_FILE%" (
    echo.
    echo  [ERROR] Blend file not found: %BLEND_FILE%
    echo.
    pause
    exit /b 1
)
echo [OK] Blend file: %BLEND_FILE%

for %%D in ("%OUT_PREFIX_ABS%") do set "OUT_DIR=%%~dpD"
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"
echo [OK] Output:     %OUT_PREFIX_ABS%####.exr

if not exist "%DONE_FILE%" type nul > "%DONE_FILE%"


:: ================================================================
::  WORK OUT WHAT IS LEFT TO RENDER  (resume)
:: ================================================================
set /a TOTAL_FRAMES=END_FRAME-START_FRAME+1
set /a ALREADY_DONE=0
for /l %%f in (%START_FRAME%,1,%END_FRAME%) do (
    findstr /x /c:"%%f" "%DONE_FILE%" >nul 2>&1 && set /a ALREADY_DONE+=1
)
set /a TO_RENDER=TOTAL_FRAMES-ALREADY_DONE

echo. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo  SESSION STARTED: %date%  %time% >> "%LOG_FILE%"
echo  Blend file: %BLEND_FILE% >> "%LOG_FILE%"
echo  Frames:     %START_FRAME% to %END_FRAME%  ^(%ALREADY_DONE% already done, %TO_RENDER% to render^) >> "%LOG_FILE%"
echo  Batch size: %BATCH_SIZE%  ^|  Cooldown: %COOLDOWN_SEC%s  ^|  Timeout: %FRAME_TIMEOUT_SEC%s x%FRAME_RETRIES% >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

echo.
echo  ================================================================
echo   BLENDER SAFE RENDER  -  %BLEND_NAME%
echo   %date%  %time%
echo   Frames : %START_FRAME% - %END_FRAME%  ^(%TOTAL_FRAMES% total^)
echo   Resume : %ALREADY_DONE% already done, %TO_RENDER% left to render
echo   Batch  : %BATCH_SIZE% frames  /  Cooldown: %COOLDOWN_SEC%s between batches
echo   Hang watchdog: %FRAME_TIMEOUT_SEC%s per frame, %FRAME_RETRIES% attempts
echo  ================================================================
echo.

if %TO_RENDER% leq 0 (
    echo  Every frame in the range is already marked done.
    echo  Delete %BLEND_BASE%_done_frames.txt to render again from scratch.
    echo.
    pause
    exit /b 0
)


:: ================================================================
::  RENDER LOOP
:: ================================================================
set /a CURRENT=%START_FRAME%
set /a IN_BATCH=0
set /a BATCH_NUM=0
set /a FRAMES_DONE=0
set /a FRAMES_FAILED=0
set /a FAILS_IN_ROW=0
set /a TOTAL_CS=0
set /a AVG_CS=0
set /a AVG_S=0
set /a AVG_D=0
set "FAILED_LIST="

:render_loop
if !CURRENT! gtr %END_FRAME% goto done

:: ---- Resume: skip frames already rendered in an earlier run ----
findstr /x /c:"!CURRENT!" "%DONE_FILE%" >nul 2>&1
if not errorlevel 1 (
    set /a CURRENT+=1
    goto render_loop
)

set "PAD=0000!CURRENT!"
set "OUT_FILE=%OUT_PREFIX_ABS%!PAD:~-4!.exr"
set /a HANDLED=FRAMES_DONE+FRAMES_FAILED+1

call :get_cs T_START
title [Rendering] Frame !CURRENT! / %END_FRAME%  ^|  !HANDLED!/%TO_RENDER%  ^|  Avg: !AVG_S!.!AVG_D!s/frame
echo [!time!]  Rendering frame !CURRENT! / %END_FRAME%  ^(!HANDLED! of %TO_RENDER% this run^) ...
echo [!time!]  Rendering frame !CURRENT! ... >> "%LOG_FILE%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0render_frame_watchdog.ps1" -Blender "%BLENDER_EXE%" -Blend "%BLEND_FILE%" -Setup "%~dp0render_gpu_setup.py" -Frame !CURRENT! -TimeoutSec %FRAME_TIMEOUT_SEC% -Retries %FRAME_RETRIES% -Log "%LOG_FILE%" -OutFile "!OUT_FILE!"
set "RC=!errorlevel!"

if not "!RC!"=="0" goto frame_failed

:: ---- Frame OK: mark it done (this is what resume reads) ----
>>"%DONE_FILE%" echo !CURRENT!
set /a FAILS_IN_ROW=0

call :get_cs T_END
set /a FRAME_CS=T_END-T_START
if !FRAME_CS! lss 0 set /a FRAME_CS+=8640000
set /a TOTAL_CS+=FRAME_CS
set /a FRAMES_DONE+=1

set /a FRAME_S=FRAME_CS/100
set /a FRAME_D=FRAME_CS%%100/10
set /a AVG_CS=TOTAL_CS/FRAMES_DONE
set /a AVG_S=AVG_CS/100
set /a AVG_D=AVG_CS%%100/10
set /a PCT=HANDLED*100/TO_RENDER

echo  ^> Frame !CURRENT! done  ^|  !HANDLED!/%TO_RENDER% ^(!PCT!%%^)  ^|  This frame: !FRAME_S!.!FRAME_D!s
echo   +-----------------------------------------+
echo   ^|  AVG RENDER TIME: !AVG_S!.!AVG_D! sec / frame
echo   +-----------------------------------------+
echo.
echo [!time!]  Frame !CURRENT! OK - !FRAME_S!.!FRAME_D!s  ^|  avg !AVG_S!.!AVG_D!s/frame  ^|  !HANDLED!/%TO_RENDER% this run >> "%LOG_FILE%"
goto after_frame


:frame_failed
set /a FRAMES_FAILED+=1
set /a FAILS_IN_ROW+=1
set "FAILED_LIST=!FAILED_LIST! !CURRENT!"
echo.
echo  ****************************************************************
echo   [FAILED] Frame !CURRENT! failed after %FRAME_RETRIES% attempts ^(code !RC!^).
echo   Skipping it for now. Run this .bat again later to retry it.
echo  ****************************************************************
echo.
echo [!time!]  FRAME !CURRENT! FAILED ^(code !RC!^) after %FRAME_RETRIES% attempts. Skipped. >> "%LOG_FILE%"

if !FAILS_IN_ROW! geq %MAX_FAILS_IN_ROW% (
    echo  ================================================================
    echo   [STOPPED] %MAX_FAILS_IN_ROW% frames failed in a row - stopping.
    echo   Failed frames:!FAILED_LIST!
    echo   Check the Blender output above and %BLEND_BASE%_render_log.txt.
    echo   Finished frames are saved; run the .bat again to resume.
    echo  ================================================================
    echo [!time!]  STOPPED - %MAX_FAILS_IN_ROW% failures in a row. Failed:!FAILED_LIST! >> "%LOG_FILE%"
    title [STOPPED] %MAX_FAILS_IN_ROW% frames failed in a row
    pause
    exit /b 1
)

:: Give the GPU / driver a full cooldown after a failure.
set /a IN_BATCH=BATCH_SIZE-1


:after_frame
set /a IN_BATCH+=1
set /a CURRENT+=1

:: ---- End of batch: cooldown, unless nothing is left ----
if !IN_BATCH! lss %BATCH_SIZE% goto render_loop
set /a IN_BATCH=0
set /a BATCH_NUM+=1

call :count_left
if !LEFT! leq 0 goto done

set /a EST_CS=LEFT*AVG_CS
set /a EST_MIN=EST_CS/100/60
set /a EST_H=EST_MIN/60
set /a EST_M=EST_MIN%%60

echo  ================================================================
echo   BATCH !BATCH_NUM! COMPLETE   ^|   Frames left: !LEFT!
echo   *** AVG TIME/FRAME:  !AVG_S!.!AVG_D! sec / frame ***
echo   Est. render left :  ~!EST_H!h !EST_M!m  ^(render time only^)
echo   Cooling down for %COOLDOWN_SEC% seconds to protect GPU...
echo  ================================================================
echo [!time!]  Batch !BATCH_NUM! complete. !LEFT! frames left. Avg !AVG_S!.!AVG_D!s/frame. Est ~!EST_H!h!EST_M!m left. Cooling %COOLDOWN_SEC%s. >> "%LOG_FILE%"

for /l %%c in (%COOLDOWN_SEC%,-1,1) do (
    title [Cooling] %%c s  ^|  Batch !BATCH_NUM! done  ^|  Avg: !AVG_S!.!AVG_D!s/frame  ^|  !LEFT! frames left
    timeout /t 1 /nobreak >nul
)
echo   Cooldown complete. Resuming render...
echo.
goto render_loop


:: ================================================================
::  DONE
:: ================================================================
:done
set /a TOTAL_S=TOTAL_CS/100
set /a TOTAL_MIN=TOTAL_S/60
set /a TOTAL_H=TOTAL_MIN/60
set /a TOTAL_M=TOTAL_MIN%%60
set /a TOTAL_R=TOTAL_S%%60

echo.
echo  ================================================================
if !FRAMES_FAILED! equ 0 (
    echo   RENDER COMPLETE  -  %BLEND_NAME%
) else (
    echo   RENDER FINISHED WITH !FRAMES_FAILED! FAILED FRAME^(S^)
)
echo   !date!  !time!
echo   ----------------------------------------------------------------
echo   Rendered this run  :  !FRAMES_DONE!
echo   Total render time  :  !TOTAL_H!h !TOTAL_M!m !TOTAL_R!s  ^(no cooldowns^)
echo   *** AVG TIME / FRAME:  !AVG_S!.!AVG_D! sec / frame ***
if !FRAMES_FAILED! gtr 0 (
    echo.
    echo   Failed frames:!FAILED_LIST!
    echo   Their EXRs are still the old playblast. Run this .bat again
    echo   to retry only those frames.
)
echo  ================================================================
echo.
echo [!time!]  RUN FINISHED - !FRAMES_DONE! rendered, !FRAMES_FAILED! failed:!FAILED_LIST!  Avg !AVG_S!.!AVG_D!s/frame. Render time !TOTAL_H!h!TOTAL_M!m!TOTAL_R!s. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

title Render finished  ^|  !FRAMES_DONE! done, !FRAMES_FAILED! failed  ^|  Avg !AVG_S!.!AVG_D!s/frame
pause
exit /b 0


:: ================================================================
::  SUBROUTINE: count_left  ->  LEFT = frames after CURRENT not yet done
:: ================================================================
:count_left
set /a LEFT=0
for /l %%f in (!CURRENT!,1,%END_FRAME%) do (
    findstr /x /c:"%%f" "%DONE_FILE%" >nul 2>&1 || set /a LEFT+=1
)
exit /b 0


:: ================================================================
::  SUBROUTINE: get_cs  -  system clock in centiseconds
:: ================================================================
:get_cs
set "_T=%time: =0%"
set /a "%1=(1%_T:~0,2%-100)*360000+(1%_T:~3,2%-100)*6000+(1%_T:~6,2%-100)*100+(1%_T:~9,2%-100)"
exit /b 0
