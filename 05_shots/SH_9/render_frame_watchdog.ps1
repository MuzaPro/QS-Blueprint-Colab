# Used by Sh09_v05_render_script.bat: renders ONE frame with a hang watchdog.
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

for ($attempt = 1; $attempt -le $Retries; $attempt++) {
    $started = Get-Date
    $p = Start-Process -FilePath $Blender -ArgumentList $argLine -NoNewWindow -PassThru
    $null = $p.Handle   # keeps the handle so ExitCode is readable later

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
    }

    if ($attempt -lt $Retries) {
        Write-Note "WATCHDOG - waiting 20 s before retrying frame $Frame."
        Start-Sleep -Seconds 20
    }
}
Write-Note "WATCHDOG - frame $Frame failed on all $Retries attempts. Giving up on it."
exit $lastCode
