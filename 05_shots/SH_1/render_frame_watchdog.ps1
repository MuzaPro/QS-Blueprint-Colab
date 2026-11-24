# Used by the shot render .bat files: renders ONE frame with a hang watchdog.
# Blender 5.2 occasionally freezes (one CPU core at 100%, GPU idle) while loading
# or finishing a frame. If a frame runs longer than -TimeoutSec, the Blender process
# is killed and the frame is retried, up to -Retries times.
#
# If -OutFile is given, a frame only counts as rendered when that file was written
# during this attempt. Blender can exit with code 0 without saving anything (e.g. GPU
# out of memory), and the old playblast EXR at the same path must not be mistaken
# for a finished render.
#
# Exit code: 0 on success, Blender's exit code if it failed, 3 if every attempt
# timed out, 4 if Blender exited OK but never wrote the output file.
param(
    [string]$Blender, [string]$Blend, [string]$Setup, [int]$Frame,
    [int]$TimeoutSec = 600, [int]$Retries = 3, [string]$Log = "", [string]$OutFile = ""
)

function Write-Note($msg) {
    $line = "[{0}]  {1}" -f (Get-Date -Format "HH:mm:ss.ff"), $msg
    Write-Host $line -ForegroundColor Yellow
    if ($Log) { Add-Content -Path $Log -Value $line }
}

$argLine = "-b --factory-startup `"$Blend`" --python `"$Setup`" -f $Frame"
$lastCode = 3

# Windows 11 throttles background processes onto the E-cores of hybrid Intel CPUs
# (i7-12700KF) as soon as another app is in the foreground. That made the CPU part of
# each frame 2-5x slower. Opt Blender out of power throttling and raise its priority.
Add-Type -Namespace Render -Name Win32 -MemberDefinition @'
[StructLayout(LayoutKind.Sequential)]
public struct PowerThrottlingState { public uint Version; public uint ControlMask; public uint StateMask; }
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool SetProcessInformation(IntPtr hProcess, int infoClass, ref PowerThrottlingState info, uint size);
'@ -ErrorAction SilentlyContinue

function Set-FullSpeed($proc) {
    try { $proc.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High } catch {}
    try {
        $s = New-Object Render.Win32+PowerThrottlingState
        $s.Version = 1; $s.ControlMask = 1; $s.StateMask = 0   # EXECUTION_SPEED: throttling off
        [void][Render.Win32]::SetProcessInformation($proc.Handle, 4, [ref]$s, 12)   # 4 = ProcessPowerThrottling
    } catch {}
}

# A killed Blender leaves its ~185 MB Cycles tile buffer in %TEMP%\blender_*. Remove the
# ones written during this attempt (the C: drive is nearly full).
function Remove-TileBuffers($since) {
    Get-ChildItem -Path $env:TEMP -Directory -Filter "blender_*" -ErrorAction SilentlyContinue |
        Where-Object { $_.CreationTime -ge $since } | ForEach-Object {
            Get-ChildItem -Path $_.FullName -Filter "cycles-tile-buffer-*.exr" -ErrorAction SilentlyContinue |
                Remove-Item -Force -ErrorAction SilentlyContinue
            if (-not (Get-ChildItem -Path $_.FullName -Force -ErrorAction SilentlyContinue)) {
                Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
            }
        }
}

for ($attempt = 1; $attempt -le $Retries; $attempt++) {
    $started = Get-Date
    $p = Start-Process -FilePath $Blender -ArgumentList $argLine -NoNewWindow -PassThru
    $null = $p.Handle   # keeps the handle so ExitCode is readable later
    Set-FullSpeed $p

    if ($p.WaitForExit($TimeoutSec * 1000)) {
        $p.WaitForExit()
        $lastCode = $p.ExitCode
        if ($lastCode -ne 0) {
            Write-Note "WATCHDOG - frame $Frame : Blender exited with code $lastCode (attempt $attempt/$Retries)."
        }
        elseif ($OutFile -and -not ((Test-Path $OutFile) -and ((Get-Item $OutFile).LastWriteTime -ge $started.AddSeconds(-2)))) {
            $lastCode = 4
            Write-Note "WATCHDOG - frame $Frame : Blender finished but did not write $OutFile (attempt $attempt/$Retries). Possible GPU out-of-memory."
        }
        else {
            exit 0
        }
    }
    else {
        $lastCode = 3
        Write-Note "WATCHDOG - frame $Frame hung for over $TimeoutSec s (attempt $attempt/$Retries). Killing Blender."
        & taskkill /PID $p.Id /T /F | Out-Null
        Start-Sleep -Seconds 2   # let Windows release the files before deleting them
        Remove-TileBuffers $started.AddSeconds(-2)
    }

    if ($attempt -lt $Retries) {
        Write-Note "WATCHDOG - waiting 20 s before retrying frame $Frame."
        Start-Sleep -Seconds 20
    }
}
Write-Note "WATCHDOG - frame $Frame failed on all $Retries attempts. Giving up on it."
exit $lastCode
