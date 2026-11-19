@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  MASTER SAFE RENDER  -  QS Blueprint  (4 jobs, overnight)
::  Gentle GPU pacing: rest time scales with how hard the GPU worked.
::
::  JOB 1  SH_12  sh_12_The_Turn_and_the_Reveal_11.blend             frames    1 -  313  (313 frames)
::  JOB 2  SH_15  sh_15_positioning_and_first_cluster_tile_18.blend  frames  117 -  550  (434 frames)
::  JOB 3  SH_18  sh_18_architecture_intro_08.blend                  frames 2740 - 3278  (539 frames)
::  JOB 4  SH_9   SH_09_factory_lights_reveal_v04.blend              frames  450 -  564  (115 frames)
::
::  Total frames: 1401
::  Render settings (engine, samples, output path, format) come from
::  each .blend file. This script only controls WHICH frames render
::  and WHEN the GPU gets to rest.
::
::  HOW THE COOLING WORKS
::  ---------------------
::  - Blender renders one frame per launch (the GPU idles while each
::    file loads, which is a free mini-break every frame).
::  - After every batch, the GPU rests for REST_PCT percent of the time
::    that batch took to render (e.g. 2 min of rendering at 40% = 48s
::    rest), never less than MIN_COOLDOWN and never more than
::    MAX_COOLDOWN. Heavy scenes automatically get longer breaks.
::  - Between blend files there is a longer BETWEEN_JOB_COOLDOWN rest.
::  - If a frame fails, the script rests, retries it once, and if it
::    still fails it logs the problem and moves on to the NEXT job
::    instead of stopping the whole night.
:: ================================================================


:: ================================================================
::  CONFIGURATION                                     <-- Edit before running
:: ================================================================

set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

::  Rest after each batch = REST_PCT % of that batch's render time,
::  clamped between MIN_COOLDOWN and MAX_COOLDOWN seconds.
set /a REST_PCT=40
set /a MIN_COOLDOWN=30
set /a MAX_COOLDOWN=180

::  Long rest between blend files (seconds).
set /a BETWEEN_JOB_COOLDOWN=300

::  Rest before retrying a failed frame (seconds).
set /a RETRY_COOLDOWN=120


:: ================================================================
::  INTERNAL PATHS                                    (do not edit)
::  %~dp0 = the folder this .bat file sits in (05_shots).
:: ================================================================

set "BASE=%~dp0"
set "BLEND_SH12=%BASE%SH_12\sh_12_The_Turn_and_the_Reveal_11.blend"
set "BLEND_SH15=%BASE%SH_15\sh_15_positioning_and_first_cluster_tile_18.blend"
set "BLEND_SH18=%BASE%SH_18\sh_18_architecture_intro_08.blend"
set "BLEND_SH09=%BASE%SH_9\SH_09_factory_lights_reveal_v04.blend"
set "LOG_FILE=%BASE%master_render_log.txt"


:: ================================================================
::  PRE-FLIGHT CHECKS  (all files are checked BEFORE anything renders,
::  so a typo is caught now instead of at 3am)
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
echo [OK] Blender: %BLENDER_EXE%

set "PREFLIGHT_FAIL=0"
call :check_file "%BLEND_SH12%" SH_12
call :check_file "%BLEND_SH15%" SH_15
call :check_file "%BLEND_SH18%" SH_18
call :check_file "%BLEND_SH09%" SH_9
if "%PREFLIGHT_FAIL%"=="1" (
    echo.
    echo  ================================================================
    echo   [ERROR] One or more blend files are missing - see above.
    echo   Nothing has been rendered.
    echo  ================================================================
    echo.
    pause
    exit /b 1
)


:: ================================================================
::  MASTER SESSION LOG HEADER
:: ================================================================

echo. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo  MASTER SESSION STARTED: %date%  %time% >> "%LOG_FILE%"
echo  Blender: %BLENDER_EXE% >> "%LOG_FILE%"
echo  Job 1: SH_12  sh_12_The_Turn_and_the_Reveal_11.blend             frames 1-313 >> "%LOG_FILE%"
echo  Job 2: SH_15  sh_15_positioning_and_first_cluster_tile_18.blend  frames 117-550 >> "%LOG_FILE%"
echo  Job 3: SH_18  sh_18_architecture_intro_08.blend                  frames 2740-3278 >> "%LOG_FILE%"
echo  Job 4: SH_9   SH_09_factory_lights_reveal_v04.blend              frames 450-564 >> "%LOG_FILE%"
echo  Rest: %REST_PCT%%% of batch time ^(%MIN_COOLDOWN%-%MAX_COOLDOWN%s^)  ^|  Between jobs: %BETWEEN_JOB_COOLDOWN%s >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

echo.
echo  ================================================================
echo   MASTER SAFE RENDER  -  QS Blueprint  -  overnight
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Job 1  :  SH_12  The_Turn_and_the_Reveal_11         frames    1-313
echo   Job 2  :  SH_15  positioning_first_cluster_tile_18  frames  117-550
echo   Job 3  :  SH_18  architecture_intro_08              frames 2740-3278
echo   Job 4  :  SH_9   factory_lights_reveal_v04          frames  450-564
echo   ----------------------------------------------------------------
echo   Rest after each batch: %REST_PCT%%% of batch render time
echo                          ^(min %MIN_COOLDOWN%s, max %MAX_COOLDOWN%s^)
echo   Between jobs: %BETWEEN_JOB_COOLDOWN%s
echo   Close this window at any time to stop.
echo  ================================================================
echo.


:: ================================================================
::  GRAND TOTAL COUNTERS
:: ================================================================

set /a GRAND_CS=0
set /a GRAND_FRAMES=0
set /a JOBS_OK=0
set "FAILED_JOBS="


:: ================================================================
::  JOB 1  -  SH_12  The Turn and the Reveal   (frames 1-313)
::  Batch size taken from SH_12\Sh_12_render_script.bat
:: ================================================================

set "JOB_BLEND=%BLEND_SH12%"
set "JOB_LABEL=SH_12_The_Turn_and_the_Reveal_11"
set /a JOB_START=1
set /a JOB_END=313
set /a BATCH_SIZE=5

call :run_job
call :after_job 1
call :between_job_cooldown


:: ================================================================
::  JOB 2  -  SH_15  Positioning and first cluster tile   (frames 117-550)
::  Batch size taken from SH_15\Sh_15_render_script.bat
:: ================================================================

set "JOB_BLEND=%BLEND_SH15%"
set "JOB_LABEL=SH_15_positioning_and_first_cluster_tile_18"
set /a JOB_START=117
set /a JOB_END=550
set /a BATCH_SIZE=8

call :run_job
call :after_job 2
call :between_job_cooldown


:: ================================================================
::  JOB 3  -  SH_18  Architecture intro   (frames 2740-3278)
::  Batch size taken from SH_18\Sh_18_render_script.bat
:: ================================================================

set "JOB_BLEND=%BLEND_SH18%"
set "JOB_LABEL=SH_18_architecture_intro_08"
set /a JOB_START=2740
set /a JOB_END=3278
set /a BATCH_SIZE=3

call :run_job
call :after_job 3
call :between_job_cooldown


:: ================================================================
::  JOB 4  -  SH_9  Factory lights reveal   (frames 450-564)
::  Batch size taken from SH_9\Sh_9_render_script.bat
:: ================================================================

set "JOB_BLEND=%BLEND_SH09%"
set "JOB_LABEL=SH_09_factory_lights_reveal_v04"
set /a JOB_START=450
set /a JOB_END=564
set /a BATCH_SIZE=3

call :run_job
call :after_job 4

goto :all_done


:: ================================================================
::  ALL JOBS FINISHED
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

if defined FAILED_JOBS (
    set "RESULT_LINE=FINISHED WITH ERRORS - failed: !FAILED_JOBS!"
) else (
    set "RESULT_LINE=ALL RENDERS COMPLETE"
)

echo.
echo  ================================================================
echo   !RESULT_LINE!
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Jobs completed OK  :  !JOBS_OK! / 4
echo   Total frames       :  !GRAND_FRAMES!
echo   Total render time  :  !GT_H!h !GT_M!m !GT_R!s  ^(render only, no cooldowns^)
echo.
echo   *** OVERALL AVG: !GRAND_AVG_S!.!GRAND_AVG_D! sec / frame ***
echo.
echo   Log file: %LOG_FILE%
echo  ================================================================
echo.

echo [%time%]  !RESULT_LINE! - !JOBS_OK!/4 jobs OK, !GRAND_FRAMES! frames, !GT_H!h!GT_M!m!GT_R!s render time, avg !GRAND_AVG_S!.!GRAND_AVG_D!s/frame. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

title !RESULT_LINE!  ^|  !GRAND_FRAMES! frames  ^|  Avg !GRAND_AVG_S!.!GRAND_AVG_D!s/frame
pause
if defined FAILED_JOBS exit /b 1
exit /b 0


:: ================================================================
::  SUBROUTINE: check_file  "<path>"  <label>
:: ================================================================
:check_file
if exist "%~1" (
    echo [OK] %2: %~1
) else (
    echo [MISSING] %2: %~1
    set "PREFLIGHT_FAIL=1"
)
exit /b 0


:: ================================================================
::  SUBROUTINE: after_job  <job number>
::  Adds the job's totals to the grand totals and records failures.
:: ================================================================
:after_job
set /a GRAND_CS+=JOB_CS
set /a GRAND_FRAMES+=JOB_FRAMES_DONE
if "!JOB_FAILED!"=="1" (
    set "FAILED_JOBS=!FAILED_JOBS! %JOB_LABEL%@frame!FAILED_FRAME!"
    echo [%time%]  Job %1 FAILED at frame !FAILED_FRAME! - continuing with next job. >> "%LOG_FILE%"
) else (
    set /a JOBS_OK+=1
)
echo [%time%]  Job %1 accumulated. Grand total so far: !GRAND_FRAMES! frames. >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
exit /b 0


:: ================================================================
::  SUBROUTINE: countdown  <seconds>  <title text>
:: ================================================================
:countdown
for /l %%c in (%1,-1,1) do (
    title [Cooling] %%c s remaining  ^|  %~2
    timeout /t 1 /nobreak >nul
)
exit /b 0


:: ================================================================
::  SUBROUTINE: between_job_cooldown
::  Extended GPU rest before loading a different blend file.
:: ================================================================
:between_job_cooldown
echo.
echo  ================================================================
echo   BETWEEN-JOB COOLDOWN  -  %BETWEEN_JOB_COOLDOWN% seconds
echo   Giving the GPU an extended rest before the next file...
echo  ================================================================
echo.
echo [%time%]  Between-job cooldown: %BETWEEN_JOB_COOLDOWN%s. >> "%LOG_FILE%"
call :countdown %BETWEEN_JOB_COOLDOWN% "Between jobs - GPU resting"
echo   Between-job cooldown complete. Loading next blend file...
echo.
echo [%time%]  Between-job cooldown complete. >> "%LOG_FILE%"
exit /b 0


:: ================================================================
::  SUBROUTINE: run_job
::  Renders a frame range from a single blend file.
::
::  Reads:  JOB_BLEND, JOB_LABEL, JOB_START, JOB_END, BATCH_SIZE
::  Sets:   JOB_CS           total centiseconds rendered this job
::          JOB_FRAMES_DONE  frames rendered this job
::          JOB_FAILED       1 if the job stopped on a failed frame
::          FAILED_FRAME     the frame that failed (if any)
:: ================================================================
:run_job

set /a TOTAL_FRAMES=JOB_END-JOB_START+1
set /a CURRENT=JOB_START
set /a IN_BATCH=0
set /a BATCH_NUM=0
set /a BATCH_CS=0
set /a FRAMES_DONE=0
set /a TOTAL_CS=0
set /a AVG_S=0
set /a AVG_D=0
set /a AVG_CS=0
set /a RETRIED=0
set "JOB_FAILED=0"
set "FAILED_FRAME="

echo. >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo  JOB: %JOB_LABEL% >> "%LOG_FILE%"
echo  Blend: %JOB_BLEND% >> "%LOG_FILE%"
echo  Frames: %JOB_START% to %JOB_END%  ^(%TOTAL_FRAMES% frames^) >> "%LOG_FILE%"
echo  Started: %date%  %time% >> "%LOG_FILE%"
echo  Batch: %BATCH_SIZE% frames  ^|  Rest: %REST_PCT%%% of batch time ^(%MIN_COOLDOWN%-%MAX_COOLDOWN%s^) >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

echo.
echo  ================================================================
echo   JOB: %JOB_LABEL%
echo   %date%  %time%
echo   Frames : %JOB_START% - %JOB_END%  ^(%TOTAL_FRAMES% frames total^)
echo   Batch  : %BATCH_SIZE% frames, then rest %REST_PCT%%% of batch time
echo  ================================================================
echo.

:job_render_loop
if !CURRENT! gtr %JOB_END% goto :job_done

call :get_cs T_START

title [Rendering] %JOB_LABEL%  ^|  Frame !CURRENT!/%JOB_END%  ^|  Avg: !AVG_S!.!AVG_D!s/frame
echo [%time%]  Rendering frame !CURRENT! / %JOB_END% ...
echo [%time%]  Rendering frame !CURRENT! ... >> "%LOG_FILE%"

"%BLENDER_EXE%" -b "%JOB_BLEND%" -f !CURRENT!

if errorlevel 1 goto :frame_failed

set /a RETRIED=0

call :get_cs T_END
set /a FRAME_CS=T_END-T_START
if !FRAME_CS! lss 0 set /a FRAME_CS+=8640000
set /a TOTAL_CS+=FRAME_CS
set /a BATCH_CS+=FRAME_CS
set /a FRAMES_DONE+=1

set /a FRAME_S=FRAME_CS/100
set /a FRAME_D=FRAME_CS%%100/10
set /a AVG_CS=TOTAL_CS/FRAMES_DONE
set /a AVG_S=AVG_CS/100
set /a AVG_D=AVG_CS%%100/10
set /a PCT=FRAMES_DONE*100/TOTAL_FRAMES

echo  ^> Frame !FRAMES_DONE!/%TOTAL_FRAMES% ^(!PCT!%%^)  ^|  This frame: !FRAME_S!.!FRAME_D!s  ^|  Avg: !AVG_S!.!AVG_D!s/frame
echo.
echo [%time%]  Frame !CURRENT! OK - !FRAME_S!.!FRAME_D!s  ^|  avg !AVG_S!.!AVG_D!s/frame  ^|  !FRAMES_DONE!/%TOTAL_FRAMES% done >> "%LOG_FILE%"

set /a IN_BATCH+=1
set /a CURRENT+=1

if !IN_BATCH! lss %BATCH_SIZE% goto :job_render_loop
if !CURRENT! gtr %JOB_END% goto :job_done

:: ---- End of batch: rest proportional to how long the batch took ----
set /a IN_BATCH=0
set /a BATCH_NUM+=1
set /a REST_SEC=BATCH_CS*REST_PCT/10000
if !REST_SEC! lss %MIN_COOLDOWN% set /a REST_SEC=MIN_COOLDOWN
if !REST_SEC! gtr %MAX_COOLDOWN% set /a REST_SEC=MAX_COOLDOWN
set /a BATCH_S=BATCH_CS/100
set /a BATCH_CS=0

set /a REMAIN_F=JOB_END-CURRENT+1
set /a EST_CS=REMAIN_F*AVG_CS
set /a EST_MIN=EST_CS/100/60
set /a EST_H=EST_MIN/60
set /a EST_M=EST_MIN%%60

echo  ================================================================
echo   BATCH !BATCH_NUM! COMPLETE  -  %JOB_LABEL%
echo   ----------------------------------------------------------------
echo   Frames done      :  !FRAMES_DONE! / %TOTAL_FRAMES%  ^(!PCT!%%^)
echo   Avg time/frame   :  !AVG_S!.!AVG_D! sec
echo   Est. render left :  ~!EST_H!h !EST_M!m for this job ^(render time only^)
echo   ----------------------------------------------------------------
echo   Batch took !BATCH_S!s  -^>  resting GPU for !REST_SEC!s
echo  ================================================================
echo.
echo [%time%]  Batch !BATCH_NUM! complete ^(!BATCH_S!s^). !FRAMES_DONE!/%TOTAL_FRAMES% done. Avg !AVG_S!.!AVG_D!s/frame. Est ~!EST_H!h!EST_M!m left. Resting !REST_SEC!s. >> "%LOG_FILE%"

call :countdown !REST_SEC! "%JOB_LABEL%  !FRAMES_DONE!/%TOTAL_FRAMES% frames  Avg !AVG_S!.!AVG_D!s/frame"

echo   Rest complete. Resuming render...
echo.
goto :job_render_loop


:: ---- A frame failed: rest, retry once, otherwise skip to next job ----
:frame_failed
if !RETRIED! equ 0 (
    set /a RETRIED=1
    echo.
    echo  ================================================================
    echo   [WARNING] Frame !CURRENT! failed. Resting %RETRY_COOLDOWN%s, then retrying once.
    echo  ================================================================
    echo.
    echo [%time%]  WARNING - Frame !CURRENT! failed in %JOB_LABEL%. Retrying after %RETRY_COOLDOWN%s. >> "%LOG_FILE%"
    call :countdown %RETRY_COOLDOWN% "Retrying frame !CURRENT! of %JOB_LABEL%"
    goto :job_render_loop
)
echo.
echo  ================================================================
echo   [ERROR] Frame !CURRENT! failed twice in %JOB_LABEL%.
echo   Skipping the rest of this job and moving on to the next one.
echo   Check the Blender output above and master_render_log.txt.
echo  ================================================================
echo.
echo [%time%]  ERROR - Frame !CURRENT! FAILED twice in %JOB_LABEL%. Job stopped. >> "%LOG_FILE%"
set "JOB_FAILED=1"
set "FAILED_FRAME=!CURRENT!"
goto :job_done


:: ================================================================
::  JOB COMPLETE
:: ================================================================
:job_done

set /a JOB_S=TOTAL_CS/100
set /a JOB_MIN=JOB_S/60
set /a JOB_H=JOB_MIN/60
set /a JOB_M=JOB_MIN%%60
set /a JOB_R=JOB_S%%60
set /a JOB_CS=TOTAL_CS
set /a JOB_FRAMES_DONE=FRAMES_DONE

if "!JOB_FAILED!"=="1" (
    set "JOB_RESULT=JOB STOPPED AT FRAME !FAILED_FRAME!"
) else (
    set "JOB_RESULT=JOB COMPLETE"
)

echo.
echo  ================================================================
echo   !JOB_RESULT!  -  %JOB_LABEL%
echo   %date%  %time%
echo   ----------------------------------------------------------------
echo   Frames rendered  :  !FRAMES_DONE! of %TOTAL_FRAMES%  ^(%JOB_START% - %JOB_END%^)
echo   Job render time  :  !JOB_H!h !JOB_M!m !JOB_R!s  ^(render only, no cooldowns^)
echo   Avg time / frame :  !AVG_S!.!AVG_D! sec
echo  ================================================================
echo.

echo [%time%]  !JOB_RESULT!: %JOB_LABEL%. !FRAMES_DONE! frames. Avg !AVG_S!.!AVG_D!s/frame. Time !JOB_H!h!JOB_M!m!JOB_R!s. >> "%LOG_FILE%"
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
