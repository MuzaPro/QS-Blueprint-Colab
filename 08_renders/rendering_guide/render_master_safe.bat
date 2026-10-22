@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  MASTER SAFE RENDER  —  Rice WaTER  (3 jobs, 3 blend files)
::  GPU overheating protection with live avg sec/frame display.
::
::  JOB 1  Seq_04_membrane_science_V2.blend       frames 2400 - 2574  (175 frames)
::  JOB 2  SH-034_B-N_Molecular_scene_V3.blend    frames    1 - 200   (200 frames)
::  JOB 3  SH_011_intro_shot_V3.blend             frames  200 - 475   (276 frames)
::
::  Total frames: ~651
::  Batch/cooldown set per job  |  Between jobs: 180s
:: ================================================================


:: ================================================================
::  CONFIGURATION                                     <-- Edit before running
:: ================================================================

set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
::  Alternative Blender paths:
::    C:\Program Files\Blender Foundation\Blender 4.3\blender.exe
::    C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
::    C:\Program Files\Blender Foundation\Blender 4.1\blender.exe

set /a BATCH_SIZE=5
set /a COOLDOWN_SEC=120
set /a BETWEEN_JOB_COOLDOWN=180


:: ================================================================
::  INTERNAL PATHS                                    (do not edit)
::  %~dp0 = the folder this .bat file sits in (project root).
::  Blend files are referenced relative to this script.
:: ================================================================

set "BASE=%~dp0"
set "BLEND_SEQ04=%BASE%06_shots\Seq_04_membrane_science\blend\Seq_04_membrane_science_V2.blend"
set "BLEND_SH034=%BASE%06_shots\SH_034_BN_Catalysis\blend\SH-034_B-N_Molecular_scene_V3.blend"
set "BLEND_SH011V3=%BASE%06_shots\SH_011_intro_shot\blend\SH_011_intro_shot_V3.blend"
set "LOG_FILE=%BASE%master_render_log.txt"


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
    echo   Looked here: %BLENDER_EXE%
    echo.
    echo   Fix: Open this .bat file and update BLENDER_EXE at the top.
    echo  ================================================================
    echo.
    pause
    exit /b 1
)

:blender_found
echo [OK] Blender:     %BLENDER_EXE%

if not exist "%BLEND_SEQ04%" (
    echo.
    echo  ================================================================
    echo   [ERROR] Seq_04 blend file not found.
    echo     %BLEND_SEQ04%
    echo  ================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] Seq_04 file: %BLEND_SEQ04%

if not exist "%BLEND_SH034%" (
    echo.
    echo  ================================================================
    echo   [ERROR] SH_034 blend file not found.
    echo     %BLEND_SH034%
    echo  ================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] SH_034 file: %BLEND_SH034%

if not exist "%BLEND_SH011V3%" (
    echo.
    echo  ================================================================
    echo   [ERROR] SH_011 V3 blend file not found.
    echo     %BLEND_SH011V3%
    echo  ================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] SH_011 V3:  %BLEND_SH011V3%


:: ================================================================
::  MASTER SESSION LOG HEADER
:: ================================================================

echo. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo  MASTER SESSION STARTED: %date%  %time%                       >> "%LOG_FILE%"
echo  Blender: %BLENDER_EXE%                                       >> "%LOG_FILE%"
echo  Job 1: Seq_04_membrane_science_V2.blend    frames 2400-2574   >> "%LOG_FILE%"
echo  Job 2: SH-034_B-N_Molecular_scene_V3.blend frames 1-200       >> "%LOG_FILE%"
echo  Job 3: SH_011_intro_shot_V3.blend          frames 200-475     >> "%LOG_FILE%"
echo  Between jobs: %BETWEEN_JOB_COOLDOWN%s  ^|  Batch/cooldown per job  >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

echo.
echo  ================================================================
echo   MASTER SAFE RENDER  —  Rice WaTER
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Job 1  :  Seq_04_membrane_science_V2.blend       frames 2400-2574
echo   Job 2  :  SH-034_B-N_Molecular_scene_V3.blend    frames    1-200
echo   Job 3  :  SH_011_intro_shot_V3.blend              frames  200-475
echo   ----------------------------------------------------------------
echo   Between jobs: %BETWEEN_JOB_COOLDOWN%s  ^|  Batch/cooldown set per job
echo  ================================================================
echo.


:: ================================================================
::  GRAND TOTAL COUNTERS
:: ================================================================

set /a GRAND_CS=0
set /a GRAND_FRAMES=0


:: ================================================================
::  JOB 1  —  Seq_04 membrane science   (frames 2400-2574,  175 frames)
:: ================================================================

set "JOB_BLEND=%BLEND_SEQ04%"
set "JOB_LABEL=Seq_04_membrane_science_V2"
set /a JOB_START=2400
set /a JOB_END=2574
set /a BATCH_SIZE=5
set /a COOLDOWN_SEC=90

call :run_job
if errorlevel 1 goto :master_abort

set /a GRAND_CS+=JOB_CS
set /a GRAND_FRAMES+=JOB_FRAMES_DONE

echo [%time%]  Job 1 accumulated. Grand total so far: %GRAND_FRAMES% frames. >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

call :between_job_cooldown


:: ================================================================
::  JOB 2  —  SH_034 BN catalysis molecular scene   (frames 1-200,  200 frames)
:: ================================================================

set "JOB_BLEND=%BLEND_SH034%"
set "JOB_LABEL=SH-034_B-N_Molecular_scene_V3"
set /a JOB_START=1
set /a JOB_END=200
set /a BATCH_SIZE=10
set /a COOLDOWN_SEC=120

call :run_job
if errorlevel 1 goto :master_abort

set /a GRAND_CS+=JOB_CS
set /a GRAND_FRAMES+=JOB_FRAMES_DONE

echo [%time%]  Job 2 accumulated. Grand total so far: %GRAND_FRAMES% frames. >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

call :between_job_cooldown


:: ================================================================
::  JOB 3  —  SH_011 intro shot V3   (frames 200-475,  276 frames)
:: ================================================================

set "JOB_BLEND=%BLEND_SH011V3%"
set "JOB_LABEL=SH_011_intro_shot_V3"
set /a JOB_START=200
set /a JOB_END=475
set /a BATCH_SIZE=5
set /a COOLDOWN_SEC=90

call :run_job
if errorlevel 1 goto :master_abort

set /a GRAND_CS+=JOB_CS
set /a GRAND_FRAMES+=JOB_FRAMES_DONE

goto :all_done


:: ================================================================
::  ALL JOBS COMPLETE
:: ================================================================
:all_done

set /a GT_S=GRAND_CS/100
set /a GT_MIN=GT_S/60
set /a GT_H=GT_MIN/60
set /a GT_M=GT_MIN%%60
set /a GT_R=GT_S%%60
set /a GRAND_AVG_CS=0
if !GRAND_FRAMES! gtr 0 set /a GRAND_AVG_CS=GRAND_CS/GRAND_FRAMES
set /a GRAND_AVG_S=GRAND_AVG_CS/100
set /a GRAND_AVG_D=GRAND_AVG_CS%%100/10

echo.
echo  ================================================================
echo   ALL RENDERS COMPLETE  —  Rice WaTER Master Render
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Jobs completed     :  3
echo   Total frames       :  %GRAND_FRAMES%
echo   Total render time  :  !GT_H!h !GT_M!m !GT_R!s  ^(render only, no cooldowns^)
echo.
echo   *** OVERALL AVG: !GRAND_AVG_S!.!GRAND_AVG_D! sec / frame ***
echo.
echo  ================================================================
echo.

echo [%time%]  ALL RENDERS COMPLETE — %GRAND_FRAMES% frames total. !GT_H!h!GT_M!m!GT_R!s render time. Avg !GRAND_AVG_S!.!GRAND_AVG_D!s/frame. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

title All Renders Complete  ^|  %GRAND_FRAMES% frames  ^|  Avg !GRAND_AVG_S!.!GRAND_AVG_D!s/frame
pause
exit /b 0


:: ================================================================
::  ABORT  —  called if any job fails
:: ================================================================
:master_abort
echo.
echo  ================================================================
echo   MASTER RENDER ABORTED
echo   One of the jobs failed — see log for details.
echo   Log file: %LOG_FILE%
echo  ================================================================
echo.
echo [%time%]  MASTER RENDER ABORTED. Grand frames so far: %GRAND_FRAMES%. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
title [STOPPED] Master render aborted — check master_render_log.txt
pause
exit /b 1


:: ================================================================
::  SUBROUTINE: between_job_cooldown
::  Extended GPU rest before loading a different blend file.
::  Uses BETWEEN_JOB_COOLDOWN (seconds).
:: ================================================================
:between_job_cooldown
echo.
echo  ================================================================
echo   BETWEEN-JOB COOLDOWN  —  %BETWEEN_JOB_COOLDOWN% seconds
echo   Giving GPU an extended rest before loading the next file...
echo  ================================================================
echo.
echo [%time%]  Between-job cooldown: %BETWEEN_JOB_COOLDOWN%s. >> "%LOG_FILE%"

for /l %%c in (%BETWEEN_JOB_COOLDOWN%,-1,1) do (
    title [Between Jobs] %%c s remaining  ^|  GPU cooling
    timeout /t 1 /nobreak >nul
)

echo   Between-job cooldown complete. Loading next blend file...
echo.
echo [%time%]  Between-job cooldown complete. >> "%LOG_FILE%"
exit /b 0


:: ================================================================
::  SUBROUTINE: run_job
::  Renders a frame range from a single blend file.
::
::  Reads:  JOB_BLEND   full path to .blend file
::          JOB_LABEL   display name for banners and log
::          JOB_START   first frame to render
::          JOB_END     last frame to render
::          BATCH_SIZE  frames per batch
::          COOLDOWN_SEC  seconds between batches
::          BLENDER_EXE   path to blender.exe
::          LOG_FILE    path to master log file
::
::  Sets:   JOB_CS          total centiseconds for this job
::          JOB_FRAMES_DONE total frames rendered this job
:: ================================================================
:run_job

set /a TOTAL_FRAMES=JOB_END-JOB_START+1
set /a CURRENT=JOB_START
set /a IN_BATCH=0
set /a BATCH_NUM=0
set /a FRAMES_DONE=0
set /a TOTAL_CS=0
set /a AVG_S=0
set /a AVG_D=0
set /a AVG_CS=0

echo. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo  JOB: %JOB_LABEL%                                             >> "%LOG_FILE%"
echo  Blend: %JOB_BLEND%                                           >> "%LOG_FILE%"
echo  Frames: %JOB_START% to %JOB_END%  ^(%TOTAL_FRAMES% frames^) >> "%LOG_FILE%"
echo  Started: %date%  %time%                                      >> "%LOG_FILE%"
echo  Batch: %BATCH_SIZE%  ^|  Cooldown: %COOLDOWN_SEC%s           >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

echo.
echo  ================================================================
echo   JOB: %JOB_LABEL%
echo   %date%  %time%
echo   Frames : %JOB_START% - %JOB_END%  ^(%TOTAL_FRAMES% frames total^)
echo   Batch  : %BATCH_SIZE% frames  /  Cooldown: %COOLDOWN_SEC%s between batches
echo  ================================================================
echo.

:job_render_loop
if %CURRENT% gtr %JOB_END% goto :job_done

:: ---- Capture start time ----
call :get_cs T_START

:: ---- Render single frame ----
title [Rendering] %JOB_LABEL%  ^|  Frame %CURRENT%/%JOB_END%  ^|  Avg: !AVG_S!.!AVG_D!s/frame
echo [%time%]  Rendering frame %CURRENT% / %JOB_END% ...
echo [%time%]  Rendering frame %CURRENT% ... >> "%LOG_FILE%"

"%BLENDER_EXE%" -b "%JOB_BLEND%" -f %CURRENT%

if errorlevel 1 (
    echo.
    echo  ================================================================
    echo   [ERROR] Frame %CURRENT% failed to render.
    echo   Job    : %JOB_LABEL%
    echo   Review the Blender output above for details.
    echo   The script has stopped safely.
    echo  ================================================================
    echo [%time%] ERROR — Frame %CURRENT% FAILED in job: %JOB_LABEL%. >> "%LOG_FILE%"
    echo.
    title [STOPPED] Error on frame %CURRENT%  ^|  %JOB_LABEL%
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

    if %CURRENT% leq %JOB_END% (

        set /a REMAIN_F=JOB_END-CURRENT+1
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
        title [Rendering] %JOB_LABEL%  ^|  Frame %CURRENT%/%JOB_END%
    )
)

goto :job_render_loop


:: ================================================================
::  JOB COMPLETE
::  Sets JOB_CS and JOB_FRAMES_DONE for grand total accumulation.
::  exit /b 0 returns to the caller of run_job.
:: ================================================================
:job_done

set /a JOB_S=TOTAL_CS/100
set /a JOB_MIN=JOB_S/60
set /a JOB_H=JOB_MIN/60
set /a JOB_M=JOB_MIN%%60
set /a JOB_R=JOB_S%%60
set /a JOB_CS=TOTAL_CS
set /a JOB_FRAMES_DONE=FRAMES_DONE

echo.
echo  ================================================================
echo   JOB COMPLETE  —  %JOB_LABEL%
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Frames rendered  :  !FRAMES_DONE!  ^(%JOB_START% - %JOB_END%^)
echo   Job render time  :  !JOB_H!h !JOB_M!m !JOB_R!s  ^(render only, no cooldowns^)
echo.
echo   *** AVG TIME / FRAME:  !AVG_S!.!AVG_D! sec / frame ***
echo.
echo  ================================================================
echo.

echo [%time%]  JOB COMPLETE: %JOB_LABEL%. !FRAMES_DONE! frames. Avg !AVG_S!.!AVG_D!s/frame. Time !JOB_H!h!JOB_M!m!JOB_R!s. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

exit /b 0


:: ================================================================
::  SUBROUTINE: get_cs
::  Converts system clock to centiseconds for per-frame timing.
:: ================================================================
:get_cs
set "_T=%time: =0%"
set /a "%1=(1%_T:~0,2%-100)*360000+(1%_T:~3,2%-100)*6000+(1%_T:~6,2%-100)*100+(1%_T:~9,2%-100)"
exit /b 0
