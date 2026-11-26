@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  BLENDER SAFE RENDER  -  TEMPLATE
::  GPU overheating protection with live avg sec/frame display.
:: ================================================================
::
::  SH_12 v15: sh_12_The_Turn_and_the_Reveal_15.blend, frames 1-462. FINAL (user, Nov 26): FHD 100%,
::  256 samples, max 60 s per frame, 60 s break after EVERY frame (RENDER_WINDOW_SEC=0), RESUME=0 overwrites the draft.
::  Advanced draft (almost final; changes may still come). Final quality
::  goes to a render farm later.
::  Output (same as the .blend's path, also forced with -o):
::    Render\sh_12_v15\sh_12_v15_####.exr
::  Samples, time limit, resolution and EXR settings come from the .blend
::  (128 samples max, 30 s per frame, 1920x1080) unless SAMPLES / RES_PCT
::  below are set. Renders on the GPU with OptiX.
::  Timed on 2026-11-26 (RTX 3080, heavy frames 380 and 585):
::    128 samples, 100%%:  ~10.4 s render, ~13.5 s per frame incl. Blender start
::    64 samples,  75%%:   ~4.9 s render,  ~8 s per frame
::  So the .blend's settings already give ~9 frames per 120 s window.
::  Breaks: frames render until RENDER_WINDOW_SEC of render time has
::  passed, then the GPU rests COOLDOWN_SEC.
::  RESUME=1 skips frames that are already rendered, so you can stop the
::  window and double-click again to continue. Delete a frame's EXR (or
::  set RESUME=0) to re-render it.
::
::  HOW TO USE THIS TEMPLATE
::  -------------------------------------------------------
::  1.  Copy this file into the SAME FOLDER as your .blend file.
::  2.  Fill in the three sections below marked  <-- EDIT THIS
::      (blend file name, frame range, and optionally batch settings).
::  3.  Double-click the .bat file to start rendering.
::
::  That's it. Everything else is handled automatically.
::
::  WHAT DOES "SAFE RENDER" MEAN?
::  -------------------------------------------------------
::  Blender renders one frame at a time and takes a short break
::  every few frames. This prevents your GPU from overheating
::  during long render sessions. The script shows you the average
::  render time per frame in real time so you always know how
::  long the job will take.
::
:: ================================================================



:: ================================================================
::  STEP 1 - YOUR BLEND FILE                          <-- EDIT THIS
:: ----------------------------------------------------------------
::  Type the name of your .blend file below (just the filename,
::  not the full path). This .bat file must be in the same folder.
::
::  Example:  set "BLEND_NAME=my_shot.blend"
:: ================================================================

set "BLEND_NAME=sh_12_The_Turn_and_the_Reveal_15.blend"


:: ================================================================
::  STEP 2 - FRAME RANGE                              <-- EDIT THIS
:: ----------------------------------------------------------------
::  Set the first and last frame you want to render.
::  You can find these numbers in Blender's Timeline or
::  Output Properties panel (camera icon in the Properties panel).
::
::  Example:  START_FRAME=1  /  END_FRAME=250  renders frames 1-250
:: ================================================================

set /a START_FRAME=1
set /a END_FRAME=462


:: ================================================================
::  STEP 3 - SAFETY SETTINGS (OPTIONAL)               <-- EDIT THIS
:: ----------------------------------------------------------------
::  RENDER_WINDOW_SEC - Render for about this many seconds, then rest.
::                      A frame that starts inside the window finishes, so
::                      a window can run a few seconds over.
::  COOLDOWN_SEC      - How many seconds the GPU rests between windows.
::
::  SAMPLES / RES_PCT - Optional overrides for this render only (the .blend
::                      is not changed). Leave empty to use the .blend's
::                      settings. If frames get slower, try SAMPLES=64 and
::                      RES_PCT=75 (approved by the user for drafts).
:: ================================================================

set /a RENDER_WINDOW_SEC=0
set /a COOLDOWN_SEC=60
set "SAMPLES=256"
set "RES_PCT=100"
:: TIME_LIMIT - max seconds of rendering per frame (Cycles time limit); empty = the .blend's
set "TIME_LIMIT=60"

:: ================================================================
::  FRAME LIST (second pass / re-renders)                <-- EDIT THIS
:: ----------------------------------------------------------------
::  Leave empty to render the whole START_FRAME..END_FRAME range.
::  Fill it to render ONLY these frames: single frames and ranges,
::  separated by spaces. Example:
::      set "FRAME_LIST=90 120-145 300 598-640"
::  To OVERWRITE frames that already exist, also set RESUME=0 below
::  (with RESUME=1 listed frames that already have an EXR are skipped).
:: ================================================================
set "FRAME_LIST="

:: Resume: 1 = skip frames that already have a real render in OUT_PREFIX, 0 = render all
set /a RESUME=0
:: Output folder (passed to Blender with -o). Same folder as the .blend's own path, so
:: renders overwrite viewport playblasts. Resume only skips REAL renders: an EXR counts
:: as rendered only if its header has Cycles' "RenderTime" stamp (playblasts don't).
set "OUT_PREFIX=%~dp0Render\sh_12_v15\sh_12_v15_"


:: ================================================================
::  BLENDER LOCATION
:: ----------------------------------------------------------------
::  This should work automatically if you installed Blender to the
::  default location. If Blender is not found, update the path below
::  to point to your blender.exe.
::
::  Common locations (copy one of these and replace the line below):
::    C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
::    C:\Program Files\Blender Foundation\Blender 4.3\blender.exe
::    C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
::    C:\Program Files\Blender Foundation\Blender 4.1\blender.exe
:: ================================================================

set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


:: ================================================================
::  !! DO NOT EDIT ANYTHING BELOW THIS LINE !!
::  The rest of the script runs automatically.
:: ================================================================


:: ----------------------------------------------------------------
::  INTERNAL PATHS
:: ----------------------------------------------------------------
::  %~dp0 means "the folder this .bat file is sitting in".
::  As long as the .bat and .blend are in the same folder, this works.
set "BLEND_FILE=%~dp0%BLEND_NAME%"
for %%F in ("%BLEND_NAME%") do set "BLEND_BASE=%%~nF"
set "LOG_FILE=%~dp0%BLEND_BASE%_render_log.txt"


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
    echo  ================================================================
    echo   [ERROR] Blender not found.
    echo.
    echo   The script looked here:
    echo     %BLENDER_EXE%
    echo.
    echo   Fix: Open this .bat file in Notepad and update the
    echo   BLENDER_EXE line near the top to the correct path.
    echo  ================================================================
    echo.
    if not defined NO_PAUSE pause
    exit /b 1
)

:blender_found
echo [OK] Blender:    %BLENDER_EXE%

if not exist "%BLEND_FILE%" (
    echo.
    echo  ================================================================
    echo   [ERROR] Blend file not found.
    echo.
    echo   The script looked for:
    echo     %BLEND_FILE%
    echo.
    echo   Fixes to check:
    echo     1. Is this .bat file in the same folder as the .blend file?
    echo     2. Is the BLEND_NAME spelling correct ^(including .blend^)?
    echo  ================================================================
    echo.
    if not defined NO_PAUSE pause
    exit /b 1
)
echo [OK] Blend file: %BLEND_FILE%


:: ================================================================
::  INITIALISE LOG FILE
:: ================================================================
echo. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo  SESSION STARTED: %date%  %time%                               >> "%LOG_FILE%"
echo  Blender:    %BLENDER_EXE%                                     >> "%LOG_FILE%"
echo  Blend file: %BLEND_FILE%                                      >> "%LOG_FILE%"
echo  Frames:     %START_FRAME% to %END_FRAME%                      >> "%LOG_FILE%"
echo  Render window: %RENDER_WINDOW_SEC%s  ^|  Cooldown: %COOLDOWN_SEC%s  ^|  Samples: %SAMPLES%  Res: %RES_PCT% ^(empty = .blend^) >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"


:: ================================================================
::  RENDER LOOP
:: ================================================================
set /a TOTAL_FRAMES=END_FRAME-START_FRAME+1

:: ---- Expand FRAME_LIST ("90 120-145") into " 90 120 121 ... " ----
set "LIST_EXP= "
if defined FRAME_LIST (
    set /a TOTAL_FRAMES=0
    for %%t in (%FRAME_LIST%) do (
        for /f "tokens=1,2 delims=-" %%a in ("%%t") do (
            if "%%b"=="" (
                set "LIST_EXP=!LIST_EXP!%%a "
                set /a TOTAL_FRAMES+=1
            ) else (
                for /l %%f in (%%a,1,%%b) do (
                    set "LIST_EXP=!LIST_EXP!%%f "
                    set /a TOTAL_FRAMES+=1
                )
            )
        )
    )
    echo [OK] Frame list: %FRAME_LIST%  ^(!TOTAL_FRAMES! frames^)
    echo  Frame list: %FRAME_LIST% >> "%LOG_FILE%"
)

echo.
echo  ================================================================
echo   BLENDER SAFE RENDER  -  %BLEND_NAME%
echo   %date%  %time%
echo   Frames : %START_FRAME% - %END_FRAME%  ^(%TOTAL_FRAMES% frames total^)
echo   Window : %RENDER_WINDOW_SEC%s of rendering  /  Cooldown: %COOLDOWN_SEC%s between windows
echo  ================================================================
echo.

set /a CURRENT=%START_FRAME%
set /a BATCH_CS=0
set /a BATCH_NUM=0
set /a WINDOW_CS=RENDER_WINDOW_SEC*100
set "PYX=import bpy;s=bpy.context.scene"
if defined SAMPLES set "PYX=!PYX!;s.cycles.samples=%SAMPLES%"
if defined RES_PCT set "PYX=!PYX!;s.render.resolution_percentage=%RES_PCT%"
if defined TIME_LIMIT set "PYX=!PYX!;s.cycles.time_limit=%TIME_LIMIT%"
set /a FRAMES_DONE=0
set /a TOTAL_CS=0
set /a AVG_S=0
set /a AVG_D=0

:render_loop
if %CURRENT% gtr %END_FRAME% goto done

:: ---- Frame list: skip frames not in the list ----
if defined FRAME_LIST if "!LIST_EXP: %CURRENT% =!"=="!LIST_EXP!" (
    set /a CURRENT+=1
    goto render_loop
)

:: ---- Zero-padded frame number, as Blender writes it (50 -> 0050) ----
set "PAD=000%CURRENT%"
set "PAD=!PAD:~-4!"

:: ---- Resume: skip frames already on disk ----
::      (a playblast EXR has no "RenderTime" in its header -> gets overwritten)
if %RESUME% equ 1 if exist "%OUT_PREFIX%!PAD!.exr" (
    findstr /m /c:"RenderTime" "%OUT_PREFIX%!PAD!.exr" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [%time%]  Frame %CURRENT% already rendered - skipping.
        set /a CURRENT+=1
        goto render_loop
    )
    echo [%time%]  Frame %CURRENT% is a playblast - will be overwritten.
)

:: ---- Capture start time ----
call :get_cs T_START

:: ---- Render single frame ----
title [Rendering] Frame %CURRENT% / %END_FRAME%  ^|  Avg: !AVG_S!.!AVG_D!s/frame
echo [%time%]  Rendering frame %CURRENT% / %END_FRAME% ...
echo [%time%]  Rendering frame %CURRENT% ... >> "%LOG_FILE%"

"%BLENDER_EXE%" -b "%BLEND_FILE%" --python-expr "!PYX!" -o "%OUT_PREFIX%####" -f %CURRENT% -- --cycles-device OPTIX

set "FRAME_FAILED="
if errorlevel 1 set "FRAME_FAILED=1"
if not exist "%OUT_PREFIX%!PAD!.exr" set "FRAME_FAILED=1"
if defined FRAME_FAILED (
    echo.
    echo  ================================================================
    echo   [ERROR] Frame %CURRENT% failed to render.
    echo   Review the Blender output above for details.
    echo   The script has stopped safely - no further frames will render.
    echo  ================================================================
    echo [%time%] ERROR - Frame %CURRENT% FAILED. Script halted. >> "%LOG_FILE%"
    echo.
    title [STOPPED] Error on frame %CURRENT% - check render_log.txt
    if not defined NO_PAUSE pause
    exit /b 1
)

:: ---- Capture end time, accumulate totals ----
call :get_cs T_END
set /a FRAME_CS=!T_END!-!T_START!
if !FRAME_CS! lss 0 set /a FRAME_CS+=8640000
set /a TOTAL_CS+=FRAME_CS
set /a FRAMES_DONE+=1

:: ---- Compute per-frame and running-average timings ----
set /a FRAME_S=FRAME_CS/100
set /a FRAME_D=FRAME_CS%%100/10
set /a AVG_CS=TOTAL_CS/FRAMES_DONE
set /a AVG_S=AVG_CS/100
set /a AVG_D=AVG_CS%%100/10
set /a PCT=FRAMES_DONE*100/TOTAL_FRAMES

:: ---- Per-frame timing display ----
echo  ^> Frame !FRAMES_DONE!/%TOTAL_FRAMES% ^(!PCT!%%^)  ^|  This frame: !FRAME_S!.!FRAME_D!s
echo.
echo   +-----------------------------------------+
echo   ^|  AVG RENDER TIME: !AVG_S!.!AVG_D! sec / frame       ^|
echo   +-----------------------------------------+
echo.
echo [%time%]  Frame %CURRENT% OK - !FRAME_S!.!FRAME_D!s  ^|  avg !AVG_S!.!AVG_D!s/frame  ^|  !FRAMES_DONE!/%TOTAL_FRAMES% done >> "%LOG_FILE%"

set /a BATCH_CS+=FRAME_CS
set /a CURRENT+=1

:: ---- End of render window: cooldown before continuing ----
if !BATCH_CS! geq !WINDOW_CS! (
    set /a BATCH_CS=0
    set /a BATCH_NUM+=1

    if %CURRENT% leq %END_FRAME% (

        :: Estimate remaining render time ^(excludes cooldown periods^)
        set /a REMAIN_F=END_FRAME-CURRENT+1
        set /a EST_CS=!REMAIN_F!*!AVG_CS!
        set /a EST_MIN=EST_CS/100/60
        set /a EST_H=EST_MIN/60
        set /a EST_M=EST_MIN%%60

        echo.
        echo  ================================================================
        echo   BATCH !BATCH_NUM! COMPLETE
        echo   ----------------------------------------------------------------
        echo   Frames done      :  !FRAMES_DONE! / %TOTAL_FRAMES%  ^(!PCT!%%^)
        echo   *** AVG TIME/FRAME:  !AVG_S!.!AVG_D! sec / frame ***
        echo   Est. render left :  ~!EST_H!h !EST_M!m  ^(render time only^)
        echo   ----------------------------------------------------------------
        echo   Cooling down for %COOLDOWN_SEC% seconds to protect GPU...
        echo  ================================================================
        echo.
        echo [%time%]  Batch !BATCH_NUM! complete. !FRAMES_DONE!/%TOTAL_FRAMES% done. Avg !AVG_S!.!AVG_D!s/frame. Est ~!EST_H!h!EST_M!m left. Cooling %COOLDOWN_SEC%s. >> "%LOG_FILE%"

        for /l %%c in (%COOLDOWN_SEC%,-1,1) do (
            title [Cooling] %%c s remaining  ^|  Batch !BATCH_NUM! done  ^|  Avg: !AVG_S!.!AVG_D!s/frame  ^|  !FRAMES_DONE!/%TOTAL_FRAMES% frames
            timeout /t 1 /nobreak >nul
        )

        echo   Cooldown complete. Resuming render...
        echo.
        echo [%time%]  Cooldown complete. Resuming. >> "%LOG_FILE%"
        title [Rendering] Frame %CURRENT% / %END_FRAME%
    )
)

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
echo   RENDER COMPLETE  -  %BLEND_NAME%
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Frames rendered    :  !FRAMES_DONE!  ^(%START_FRAME% - %END_FRAME%^)
echo   Total render time  :  !TOTAL_H!h !TOTAL_M!m !TOTAL_R!s  ^(render only, no cooldowns^)
echo.
echo   *** AVG TIME / FRAME:  !AVG_S!.!AVG_D! sec / frame ***
echo.
echo  ================================================================
echo.
echo [%time%]  RENDER COMPLETE - !FRAMES_DONE! frames done. Avg !AVG_S!.!AVG_D!s/frame. Total render time !TOTAL_H!h!TOTAL_M!m!TOTAL_R!s. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

title Render Complete  ^|  !FRAMES_DONE! frames  ^|  Avg !AVG_S!.!AVG_D!s/frame
if not defined NO_PAUSE pause
exit /b 0


:: ================================================================
::  SUBROUTINE: get_cs
::  Reads the system clock and converts it to centiseconds.
::  (Used internally for per-frame timing - do not edit.)
:: ================================================================
:get_cs
set "_T=%time: =0%"
set /a "%1=(1%_T:~0,2%-100)*360000+(1%_T:~3,2%-100)*6000+(1%_T:~6,2%-100)*100+(1%_T:~9,2%-100)"
exit /b 0
