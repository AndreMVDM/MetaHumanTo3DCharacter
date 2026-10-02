$ErrorActionPreference = 'Stop'
$panelRoot = Split-Path -Parent $PSCommandPath
$panelUrl = 'http://127.0.0.1:8746'
$panelRunning = $false
try { $panelResponse = Invoke-RestMethod -Uri "$panelUrl/api/status" -TimeoutSec 2; $panelRunning = $true } catch {}
if (-not $panelRunning) {
    $panelPython = (Get-Command python).Source
    Start-Process -FilePath $panelPython -ArgumentList @('-B', ('"' + (Join-Path $panelRoot 'server.py') + '"')) -WindowStyle Hidden
    for ($panelAttempt = 0; $panelAttempt -lt 20; $panelAttempt++) {
        Start-Sleep -Milliseconds 200
        try { Invoke-RestMethod -Uri "$panelUrl/api/status" -TimeoutSec 1 | Out-Null; break } catch {}
    }
}
Start-Process $panelUrl
