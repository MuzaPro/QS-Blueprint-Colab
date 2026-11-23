# Used by Sh01_render_script.bat: renders ONE frame with a hang watchdog.
# Blender 5.2 occasionally freezes (one CPU core at 100%, GPU idle) while loading
# or finishing a frame. If a frame runs longer than -TimeoutSec, the Blender process
# is killed and the frame is retried, up to -Retries times.
# Exit code: Blender's own exit code, or 3 if every attempt timed out.
param(
    [string]$Blender, [string]$Blend, [string]$Setup, [int]$Frame,
    [int]$TimeoutSec = 300, [int]$Retries = 3, [string]$Log = ""
)

function Write-Note($msg) {
    $line = "[{0}]  {1}" -f (Get-Date -Format "HH:mm:ss.ff"), $msg
    Write-Host $line -ForegroundColor Yellow
    if ($Log) { Add-Content -Path $Log -Value $line }
}

$argLine = "-b --factory-startup `"$Blend`" --python `"$Setup`" -f $Frame"

for ($attempt = 1; $attempt -le $Retries; $attempt++) {
    $p = Start-Process -FilePath $Blender -ArgumentList $argLine -NoNewWindow -PassThru
    $null = $p.Handle   # keeps the handle so ExitCode is readable later
    if ($p.WaitForExit($TimeoutSec * 1000)) {
        $p.WaitForExit()
        exit $p.ExitCode
    }
    Write-Note "WATCHDOG - frame $Frame hung for over $TimeoutSec s (attempt $attempt/$Retries). Killing Blender and retrying."
    & taskkill /PID $p.Id /T /F | Out-Null
    Start-Sleep -Seconds 5
}
Write-Note "WATCHDOG - frame $Frame hung on all $Retries attempts. Giving up."
exit 3
