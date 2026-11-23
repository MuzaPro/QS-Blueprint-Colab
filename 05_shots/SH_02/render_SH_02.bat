@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  BLENDER SAFE RENDER  —  TEMPLATE
::  GPU overheating protection with live avg sec/frame display.
:: ================================================================
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
::  STEP 1 — YOUR BLEND FILE                          <-- EDIT THIS
:: ----------------------------------------------------------------
::  Type the name of your .blend file below (just the filename,
::  not the full path). This .bat file must be in the same folder.
::
::  Example:  set "BLEND_NAME=my_shot.blend"
:: ================================================================

set "BLEND_NAME=SH_02_Tweezers_and_logic_grid_v02.blend"


:: ================================================================
::  STEP 2 — SCENES, FRAME RANGES, OUTPUT                <-- EDIT THIS
:: ----------------------------------------------------------------
::  This blend has TWO scenes that share the same camera move:
::    Scene      = atomic layer (tweezers, atoms, vacuum chamber)
::    Scene.001  = logic layer  (qubit icons, wireframe reveal)
::  Both are rendered one after the other, each to its own folder.
::  The edit (crossfade around frame 100-120) is done later in comp.
::
::  RENDER_ROOT  — where the frame folders are created.
::                 The _v02 folders keep the earlier renders untouched.
::  SKIP_EXISTING=1 skips frames whose .exr already exists, so you
::                 can stop the script and re-run it to resume.
:: ================================================================

set "RENDER_ROOT=%~dp0..\..\08_renders\Final_draft"

set "SCENE_A=Scene"
set /a A_START=1
set /a A_END=177
set "A_OUT=sh_02_tweezers_v02\SH_02_tweezers_"

set "SCENE_B=Scene.001"
set /a B_START=75
set /a B_END=250
set "B_OUT=sh_02_logic_v02\SH_02_logic_space_"

set /a SKIP_EXISTING=1

:: ================================================================
::  STEP 3 — SAFETY SETTINGS (OPTIONAL)               <-- EDIT THIS
:: ----------------------------------------------------------------
::  BATCH_SIZE   — Number of frames rendered before each break.
::                 Lower = more breaks = cooler GPU.
::                 Recommended: 5 (default). Use 2-3 for heavy scenes.
::
::  COOLDOWN_SEC — How many seconds to wait between batches.
::                 Recommended: 120 (2 minutes).
::                 Increase to 180-300 if your GPU runs very hot.
:: ================================================================

set /a BATCH_SIZE=4
set /a COOLDOWN_SEC=30


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
    pause
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
    pause
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
echo  Scenes:     %SCENE_A% %A_START%-%A_END%  then  %SCENE_B% %B_START%-%B_END% >> "%LOG_FILE%"
echo  Batch size: %BATCH_SIZE%  ^|  Cooldown: %COOLDOWN_SEC%s       >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"


:: ================================================================
::  RENDER BOTH SCENES
:: ================================================================
call :render_scene "%SCENE_A%" %A_START% %A_END% "%A_OUT%"
if errorlevel 1 exit /b 1
call :render_scene "%SCENE_B%" %B_START% %B_END% "%B_OUT%"
if errorlevel 1 exit /b 1

echo.
echo  ================================================================
echo   ALL SCENES COMPLETE  —  %BLEND_NAME%
echo   Atomic layer : %RENDER_ROOT%\%A_OUT%####.exr
echo   Logic layer  : %RENDER_ROOT%\%B_OUT%####.exr
echo  ================================================================
echo [%time%]  ALL SCENES COMPLETE >> "%LOG_FILE%"
title Render Complete  ^|  both scenes
pause
exit /b 0


:: ================================================================
::  SUBROUTINE: render_scene  "SceneName" START END "out\prefix_"
:: ================================================================
:render_scene
set "SCENE=%~1"
set /a START_FRAME=%2
set /a END_FRAME=%3
set "OUT_PREFIX=%RENDER_ROOT%\%~4"
set /a TOTAL_FRAMES=END_FRAME-START_FRAME+1
echo ---- SCENE %SCENE%  frames %START_FRAME%-%END_FRAME%  ->  %OUT_PREFIX%####.exr >> "%LOG_FILE%"

echo.
echo  ================================================================
echo   BLENDER SAFE RENDER  —  %BLEND_NAME%  [%SCENE%]
echo   %date%  %time%
echo   Frames : %START_FRAME% - %END_FRAME%  ^(%TOTAL_FRAMES% frames total^)
echo   Batch  : %BATCH_SIZE% frames  /  Cooldown: %COOLDOWN_SEC%s between batches
echo  ================================================================
echo.

set /a CURRENT=%START_FRAME%
set /a IN_BATCH=0
set /a BATCH_NUM=0
set /a FRAMES_DONE=0
set /a TOTAL_CS=0
set /a AVG_S=0
set /a AVG_D=0

:render_loop
if %CURRENT% gtr %END_FRAME% goto done

:: ---- Resume support: skip frames already on disk ----
set "PAD=000%CURRENT%"
set "PAD=!PAD:~-4!"
if %SKIP_EXISTING% equ 1 if exist "%OUT_PREFIX%!PAD!.exr" (
    echo [%time%]  [%SCENE%] frame %CURRENT% exists — skipped
    set /a CURRENT+=1
    goto render_loop
)

:: ---- Capture start time ----
call :get_cs T_START

:: ---- Render single frame ----
title [%SCENE%] Frame %CURRENT% / %END_FRAME%  ^|  Avg: !AVG_S!.!AVG_D!s/frame
echo [%time%]  [%SCENE%] Rendering frame %CURRENT% / %END_FRAME% ...
echo [%time%]  [%SCENE%] Rendering frame %CURRENT% ... >> "%LOG_FILE%"

:: --factory-startup: no user add-ons in the render (they error on load / every frame)
:: render_gpu_setup.py: re-enables OptiX, which factory startup resets to CPU
:: -S picks the scene, -o sends frames to the _v02 folder (format stays EXR from the scene)
"%BLENDER_EXE%" -b --factory-startup "%BLEND_FILE%" -S "%SCENE%" --python "%~dp0render_gpu_setup.py" -o "%OUT_PREFIX%####" -f %CURRENT%

if errorlevel 1 (
    echo.
    echo  ================================================================
    echo   [ERROR] Frame %CURRENT% failed to render.
    echo   Review the Blender output above for details.
    echo   The script has stopped safely — no further frames will render.
    echo  ================================================================
    echo [%time%] ERROR — Frame %CURRENT% FAILED. Script halted. >> "%LOG_FILE%"
    echo.
    title [STOPPED] Error on frame %CURRENT% — check render_log.txt
    pause
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
echo [%time%]  Frame %CURRENT% OK — !FRAME_S!.!FRAME_D!s  ^|  avg !AVG_S!.!AVG_D!s/frame  ^|  !FRAMES_DONE!/%TOTAL_FRAMES% done >> "%LOG_FILE%"

set /a IN_BATCH+=1
set /a CURRENT+=1

:: ---- End-of-batch: cooldown before continuing ----
if !IN_BATCH! equ %BATCH_SIZE% (
    set /a IN_BATCH=0
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
echo   SCENE COMPLETE  —  %BLEND_NAME%  [%SCENE%]
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Frames rendered    :  !FRAMES_DONE!  ^(%START_FRAME% - %END_FRAME%^)
echo   Total render time  :  !TOTAL_H!h !TOTAL_M!m !TOTAL_R!s  ^(render only, no cooldowns^)
echo.
echo   *** AVG TIME / FRAME:  !AVG_S!.!AVG_D! sec / frame ***
echo.
echo  ================================================================
echo.
echo [%time%]  [%SCENE%] SCENE COMPLETE — !FRAMES_DONE! frames done. Avg !AVG_S!.!AVG_D!s/frame. Total render time !TOTAL_H!h!TOTAL_M!m!TOTAL_R!s. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

exit /b 0


:: ================================================================
::  SUBROUTINE: get_cs
::  Reads the system clock and converts it to centiseconds.
::  (Used internally for per-frame timing — do not edit.)
:: ================================================================
:get_cs
set "_T=%time: =0%"
set /a "%1=(1%_T:~0,2%-100)*360000+(1%_T:~3,2%-100)*6000+(1%_T:~6,2%-100)*100+(1%_T:~9,2%-100)"
exit /b 0
