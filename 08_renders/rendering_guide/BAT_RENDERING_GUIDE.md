# Bat Rendering Guide — Agent Instructions

> **Purpose:** This document defines exactly how to write a Blender safe-render `.bat` file for this project.  
> When an agent receives a blend file path and a frame range, it should produce a `.bat` file that fully matches the conventions below — no deviation, no simplification.

---

## What to ask me before writing the file

If any of the following are not provided, ask:

| Parameter | Default if not stated |
|---|---|
| Blend file path | Required — do not guess |
| Frame range (start / end) | Required — do not guess |
| Batch size (frames per batch) | **5** |
| Cooldown duration (seconds) | **120** |
| Blender version | **5.0** (update the comment list if a newer version is being used) |

---

## File placement

**Place the `.bat` file in the same directory as the `.blend` file it renders.**  
Use `%~dp0` as the base path for all file references so the script is portable regardless of where the folder sits on disk.

The log file must also land in the same directory, named `render_log_<shortname>.txt` where `<shortname>` is a brief identifier derived from the blend file name (e.g. `render_log_seq05.txt` for `seq_05_city_in_the_lab.blend`).

---

## File naming

Name the bat file: `render_<shortname>_safe.bat`

Examples:
- `seq_05_city_in_the_lab.blend` → `render_seq05_safe.bat`
- `sh013_phage_bench.blend` → `render_sh013_safe.bat`

---

## Script structure (in order)

### 1. Header block

```bat
@echo off
setlocal enabledelayedexpansion
```

Follow with a wide comment banner (use `=` rows, 64 chars) that states:
- The blend file being rendered
- Frame range, batch size, cooldown
- One-line purpose statement: `GPU overheating protection with live avg sec/frame display.`

### 2. CONFIGURATION section

Label it clearly with `<-- Edit before running`. Contains only:

```bat
set /a START_FRAME=<start>
set /a END_FRAME=<end>
```

Blender executable with commented alternative paths for Blender 4.1, 4.2, 4.3, 5.0:

```bat
set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
```

Batch size and cooldown, with a note that these match the project brief:

```bat
set /a BATCH_SIZE=5
set /a COOLDOWN_SEC=120
```

### 3. INTERNAL PATHS section

Label it `(do not edit)`. Uses `%~dp0` so paths are always relative to the script's own directory:

```bat
set "BLEND_FILE=%~dp0<blend_filename>.blend"
set "LOG_FILE=%~dp0render_log_<shortname>.txt"
```

### 4. PRE-FLIGHT CHECKS

Two checks, in order:

**a) Blender executable check** — if the configured path does not exist, fall back to `where blender` on `%PATH%`. If neither works, print a clear error box and `pause` then `exit /b 1`. On success jump to `:blender_found` and print `[OK] Blender: <path>`.

**b) Blend file check** — if `%BLEND_FILE%` does not exist, print an error box with the exact path, `pause`, `exit /b 1`. On success print `[OK] Blend file: <path>`.

### 5. LOG FILE INITIALISATION

Append a session header to the log file before the first frame renders:

```
================================================================
 SESSION STARTED: <date>  <time>
 Blender:    <path>
 Blend file: <path>
 Frames:     <start> to <end>
 Batch size: <n>  |  Cooldown: <n>s
================================================================
```

### 6. RENDER LOOP — variable initialisation

Before `:render_loop`, initialise:

```bat
set /a TOTAL_FRAMES=END_FRAME-START_FRAME+1
set /a CURRENT=%START_FRAME%
set /a IN_BATCH=0
set /a BATCH_NUM=0
set /a FRAMES_DONE=0
set /a TOTAL_CS=0
set /a AVG_S=0
set /a AVG_D=0
```

Print a startup banner showing blend name, date/time, frame range + total count, batch / cooldown settings.

### 7. RENDER LOOP — per-frame logic

At the top of `:render_loop`, check `if %CURRENT% gtr %END_FRAME% goto done`.

**For each frame:**

1. Call `:get_cs T_START` to record the start timestamp in centiseconds.
2. Set the window title: `[Rendering] Frame <n> / <end>  |  Avg: <avg_s>.<avg_d>s/frame`
3. Run: `"%BLENDER_EXE%" -b "%BLEND_FILE%" -f %CURRENT%`
4. On `errorlevel 1`: print error box, log the failure, set title to `[STOPPED] Error on frame <n>`, `pause`, `exit /b 1`.
5. Call `:get_cs T_END`, compute `FRAME_CS` using **delayed expansion**: `set /a FRAME_CS=!T_END!-!T_START!`. Handle midnight rollover: `if !FRAME_CS! lss 0 set /a FRAME_CS+=8640000`.
6. Accumulate `TOTAL_CS += FRAME_CS`, increment `FRAMES_DONE`.
7. Compute display values using integer arithmetic only (no floating point):
   - `FRAME_S = FRAME_CS / 100`  (whole seconds for this frame)
   - `FRAME_D = FRAME_CS %% 100 / 10`  (tenths digit)
   - `AVG_CS = TOTAL_CS / FRAMES_DONE`
   - `AVG_S = AVG_CS / 100`
   - `AVG_D = AVG_CS %% 100 / 10`
   - `PCT = FRAMES_DONE * 100 / TOTAL_FRAMES`
8. Print the per-frame summary — **this is the most important visual element**:

```
 > Frame <done>/<total> (<pct>%)  |  This frame: <frame_s>.<frame_d>s

   +-----------------------------------------+
   |  AVG RENDER TIME: <avg_s>.<avg_d> sec / frame       |
   +-----------------------------------------+

```

9. Append to log: `Frame <n> OK — <frame_s>.<frame_d>s  |  avg <avg_s>.<avg_d>s/frame  |  <done>/<total> done`
10. Increment `IN_BATCH` and `CURRENT`.

### 8. RENDER LOOP — end-of-batch cooldown

After incrementing, check `if !IN_BATCH! equ %BATCH_SIZE%`. If true:

- Reset `IN_BATCH=0`, increment `BATCH_NUM`.
- Only show the cooldown block if there are more frames to render (`if %CURRENT% leq %END_FRAME%`).
- Compute estimated remaining render time using **delayed expansion and a minutes-first chain** to avoid integer overflow:

```bat
set /a REMAIN_F=END_FRAME-CURRENT+1
set /a EST_CS=!REMAIN_F!*!AVG_CS!
set /a EST_MIN=EST_CS/100/60
set /a EST_H=EST_MIN/60
set /a EST_M=EST_MIN%%60
```
- Print a batch-complete banner:

```
 ================================================================
  BATCH <n> COMPLETE
  ----------------------------------------------------------------
  Frames done      :  <done> / <total>  (<pct>%)
  *** AVG TIME/FRAME:  <avg_s>.<avg_d> sec / frame ***
  Est. render left :  ~<h>h <m>m  (render time only)
  ----------------------------------------------------------------
  Cooling down for <cooldown> seconds to protect GPU...
 ================================================================
```

- Append to log: batch number, frames done, avg, estimate, cooldown duration.
- Countdown using `for /l %%c in (%COOLDOWN_SEC%,-1,1)`:
  - Update title each second: `[Cooling] <n>s remaining  |  Batch <b> done  |  Avg: <avg_s>.<avg_d>s/frame  |  <done>/<total> frames`
  - Use `timeout /t 1 /nobreak >nul`
- After countdown: print `Cooldown complete. Resuming render...`, log it, restore rendering title.

### 9. DONE block

```bat
:done
```

Compute total render time using a **safe minutes-first chain** (avoids integer overflow on long renders):

```bat
set /a TOTAL_S=TOTAL_CS/100
set /a TOTAL_MIN=TOTAL_S/60
set /a TOTAL_H=TOTAL_MIN/60
set /a TOTAL_M=TOTAL_MIN%%60
set /a TOTAL_R=TOTAL_S%%60
```

Do **not** compute `TOTAL_CS / 360000` directly for hours — this loses seconds precision and produces wrong results on long renders.

Print a final summary banner:

```
 ================================================================
  RENDER COMPLETE  —  <blend short name>
  <date>  <time>
  ----------------------------------------------------------------
  Frames rendered    :  <n>  (<start> - <end>)
  Total render time  :  <h>h <m>m <s>s  (render only, no cooldowns)

  *** AVG TIME / FRAME:  <avg_s>.<avg_d> sec / frame ***

 ================================================================
```

Append equivalent summary to log, close the log session with a `===` row.

Set window title: `Render Complete  |  <n> frames  |  Avg <avg_s>.<avg_d>s/frame`

End with `pause` then `exit /b 0`.

### 10. :get_cs subroutine

Always include this at the bottom of the file. It converts `%time%` to centiseconds:

```bat
:get_cs
set "_T=%time: =0%"
set /a "%1=(1%_T:~0,2%-100)*360000+(1%_T:~3,2%-100)*6000+(1%_T:~6,2%-100)*100+(1%_T:~9,2%-100)"
exit /b 0
```

This handles locale-safe parsing and leading-space padding in single-digit hours.

---

## Visual design rules

- Section dividers: `=` rows inside `echo` statements, 64 characters wide.
- Sub-dividers: `-` rows inside `echo` statements.
- The **avg sec/frame box** (the `+---+` / `| AVG RENDER TIME |` box) must appear after **every single frame**, not just at batch boundaries. This is the primary feedback the user cares about.
- The batch-complete summary repeats the avg prominently with triple asterisks: `*** AVG TIME/FRAME: X.Xs / frame ***`.
- The final done summary also uses triple asterisks: `*** AVG TIME / FRAME: X.Xs / frame ***`.
- Window title bar always reflects current state: `[Rendering]`, `[Cooling]`, `[STOPPED]`, or `Render Complete`.

---

## Integer math conventions

All timing is in centiseconds (hundredths of a second) internally. Never use floating point or external tools like `powershell` for math. Display tenths precision using `%%100/10`.

When computing `FRAME_CS` from subroutine output, always use delayed expansion: `set /a FRAME_CS=!T_END!-!T_START!` — **not** bare variable names like `T_END - T_START`. This ensures the values set by `call :get_cs` are resolved correctly.

When converting centiseconds to h/m/s, always use the minutes-first chain (see DONE block above). Do not divide centiseconds directly by 360000 for hours.

---

## Parenthesis escaping rules (critical)

In cmd.exe batch files with `setlocal enabledelayedexpansion`, any literal `(` or `)` characters inside a compound `if (...)` or `for (...)` block **must be escaped** as `^(` and `^)`. Unescaped parentheses inside a compound block cause the batch parser to misread the block structure, which can make the script exit silently after one frame with no visible error.

This applies everywhere inside a compound block — including inside `echo` statements:

```bat
:: CORRECT — parentheses escaped inside compound block
if !IN_BATCH! equ %BATCH_SIZE% (
    echo   Frames done : !FRAMES_DONE! / %TOTAL_FRAMES%  ^(!PCT!%%^)
    echo   Est. left   : ~!EST_H!h !EST_M!m  ^(render time only^)
)

:: WRONG — unescaped parentheses break block parsing silently
if !IN_BATCH! equ %BATCH_SIZE% (
    echo   Frames done : !FRAMES_DONE! / %TOTAL_FRAMES%  (!PCT!%%)
    echo   Est. left   : ~!EST_H!h !EST_M!m  (render time only)
)
```

This rule applies even when the parentheses are balanced within the same echo line. The parser counts them structurally before variable expansion occurs.

---

## Error handling rules

- Any non-zero Blender exit code stops the script immediately.
- The user is shown a clear box error with the failed frame number.
- No frames are silently skipped.
- The log always records the failure before pausing.

---

## Log file conventions

- Always **append** to the log (`>>`), never overwrite. Multiple render sessions accumulate in the same file.
- Each session is bounded by `===` header and footer rows.
- Every frame gets one log line: timestamp, frame number, result (OK or FAILED), this-frame time, running avg, progress fraction.
- Batch events and cooldown events are also logged with timestamps.

---

## Default values for this project

| Setting | Value |
|---|---|
| Batch size | 5 frames |
| Cooldown | 120 seconds |
| Blender | 5.0 (path: `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`) |
| Fallback Blender search | `where blender` on `%PATH%` |

---

## Checklist before delivering the bat file

- [ ] File is placed (or would be placed) in the same folder as the `.blend` file
- [ ] `%~dp0` used for all paths — no hardcoded absolute directories except Blender exe
- [ ] Frame range matches the request exactly
- [ ] Avg sec/frame box prints after every single frame
- [ ] Batch cooldown block only fires when more frames remain
- [ ] `FRAME_CS` computed with delayed expansion: `set /a FRAME_CS=!T_END!-!T_START!`
- [ ] Midnight rollover guard uses delayed expansion: `if !FRAME_CS! lss 0 set /a FRAME_CS+=8640000`
- [ ] ETA inside batch block uses delayed expansion and minutes-first chain: `EST_CS=!REMAIN_F!*!AVG_CS!` → `EST_MIN=EST_CS/100/60` → `EST_H/EST_M`
- [ ] All literal `(` and `)` inside compound `if`/`for` blocks are escaped as `^(` and `^)`
- [ ] DONE block uses minutes-first chain: `TOTAL_S=TOTAL_CS/100` → `TOTAL_MIN` → `TOTAL_H/TOTAL_M/TOTAL_R`
- [ ] `:get_cs` subroutine included at bottom of file
- [ ] Log file appends, never overwrites
- [ ] Pre-flight checks for both Blender exe and blend file
- [ ] `pause` before every `exit /b 1` so errors are readable
- [ ] Final `pause` before `exit /b 0` so the window stays open

---

## Master render script — multi-file queue

`render_master_safe.bat` lives at the **project root** and renders multiple blend files (or multiple frame ranges from the same blend file) in sequence, with GPU cooldown between every batch and an extended cooldown between jobs.

The file for this project is: `render_master_safe.bat`  
Its log writes to: `master_render_log.txt` (also at project root)

---

### How the queue works

All render logic lives in a single `:run_job` subroutine. Before each `call :run_job`, four variables are set to describe the job:

| Variable | What it holds |
|---|---|
| `JOB_BLEND` | Full path to the `.blend` file |
| `JOB_LABEL` | Short display name shown in banners and the log |
| `JOB_START` | First frame to render |
| `JOB_END` | Last frame to render |

The subroutine runs the full per-frame loop (batch cooldowns included) for those settings and then returns. Grand-total counters (`GRAND_CS`, `GRAND_FRAMES`) are accumulated after each job. An extended between-job cooldown fires between consecutive jobs.

**How cmd.exe handles this:** `call :run_job` pushes a return address onto cmd's internal call stack. Inside the subroutine, `goto :job_render_loop` loops freely and `goto :job_done` exits the loop — both without touching the call stack. The `exit /b 0` at `:job_done` pops the return address and lands back at the line after `call :run_job`. Variables set inside the subroutine (including `JOB_CS` and `JOB_FRAMES_DONE`) persist because there is only one `setlocal` scope for the whole file.

---

### Configuration variables (top of file)

```bat
set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
set /a BATCH_SIZE=5
set /a COOLDOWN_SEC=120          :: between-batch cooldown (seconds)
set /a BETWEEN_JOB_COOLDOWN=180  :: between-job cooldown (seconds)
```

`BETWEEN_JOB_COOLDOWN` should be longer than `COOLDOWN_SEC` — Blender unloads the old scene and loads the new one during this window, which is heavier on the GPU than a simple frame break.

---

### Adding a new job to the queue

Insert a new block **before** the `goto :all_done` line, following the exact pattern below. Copy an existing job block and edit the four variables:

```bat
:: ================================================================
::  JOB <N>  —  <short description>  (frames <start>-<end>,  <count> frames)
:: ================================================================

set "JOB_BLEND=%BASE%06_shots\<shot_folder>\blend\<filename>.blend"
set "JOB_LABEL=<filename_without_extension>  [optional note e.g. Pass 1 of 2]"
set /a JOB_START=<start_frame>
set /a JOB_END=<end_frame>

call :run_job
if errorlevel 1 goto :master_abort

set /a GRAND_CS+=JOB_CS
set /a GRAND_FRAMES+=JOB_FRAMES_DONE

echo [%time%]  Job <N> accumulated. Grand total so far: %GRAND_FRAMES% frames. >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

call :between_job_cooldown
```

**Omit the final `call :between_job_cooldown`** on the very last job in the queue (no cooldown needed after the last file).

If a single blend file has multiple non-contiguous frame ranges (like SH_031's two animation sequences), create one job block per range — they all point to the same `JOB_BLEND` path. No `PASS_NUM` variable is needed; the separate job blocks handle sequencing explicitly.

---

### Pre-flight checks — adding a new blend file

For every unique blend file added to the queue, add a matching pre-flight check in the PRE-FLIGHT CHECKS section near the top of the file:

```bat
set "BLEND_<SHORTNAME>=%BASE%06_shots\<folder>\blend\<filename>.blend"

...

if not exist "%BLEND_<SHORTNAME>%" (
    echo.
    echo  ================================================================
    echo   [ERROR] <SHORTNAME> blend file not found.
    echo     %BLEND_<SHORTNAME>%
    echo  ================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] <SHORTNAME> file: %BLEND_<SHORTNAME>%
```

Also add the blend file to the master session log header block that follows the checks.

---

### What to ask before adding a job

| Parameter | Default if not stated |
|---|---|
| Blend file path (relative to project root) | Required — do not guess |
| Frame range (start / end) | Required — do not guess |
| Is this a new blend file or the same as an existing job? | Required — affects pre-flight and path variables |
| Position in the queue (after which existing job?) | Required |
| Between-job cooldown after this job? | Yes, unless it is the last job |

---

### Checklist before delivering an updated master script

- [ ] New `BLEND_<SHORTNAME>` path variable declared in INTERNAL PATHS
- [ ] Pre-flight check for the new blend file added (if it is a new file)
- [ ] New blend file listed in the master session log header
- [ ] New job block uses `JOB_BLEND`, `JOB_LABEL`, `JOB_START`, `JOB_END` — no other frame/path variables
- [ ] `call :run_job` immediately followed by `if errorlevel 1 goto :master_abort`
- [ ] Grand total accumulation lines present after every job
- [ ] `call :between_job_cooldown` present after every job **except the last**
- [ ] `goto :all_done` still appears immediately before the subroutine definitions
