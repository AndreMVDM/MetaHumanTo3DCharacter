param([string]$EngineDirectory = 'D:\Epic Games\UE_5.8')
$ErrorActionPreference = 'Stop'
$r2Directory = $PSScriptRoot
$projectDirectory = (Resolve-Path -LiteralPath "$r2Directory\..\..\..\..\..").Path
$evidenceDirectory = Join-Path $projectDirectory 'Documentation\Phase4F\Benchmark\Runs\01_FemaleBodyRigged\R2_EndToEnd'
$authorProject = Join-Path $r2Directory 'AuthoringHost\AuthoringHost.uproject'

function Invoke-R2Process([string]$Executable, [string[]]$Arguments, [string]$LogName) {
    $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $r2Directory "$LogName.stdout.log") `
        -RedirectStandardError (Join-Path $r2Directory "$LogName.stderr.log")
    try {
        Wait-Process -Id $process.Id -Timeout 600
        $process.Refresh()
        if ($process.ExitCode -ne 0) { throw "$LogName process failed with exit code $($process.ExitCode)" }
    } catch {
        # Only stop the exact process launched by this invocation.
        if (-not $process.HasExited) { Stop-Process -Id $process.Id }
        throw
    }
}

# The task's baseline predates implementation. For a subsequent reproducibility
# run choose a NEW output_namespace; existing outputs/evidence are never repaired.
if (-not (Test-Path -LiteralPath (Join-Path $evidenceDirectory 'baseline.json'))) { throw 'Preservation baseline is missing' }
if (-not (Test-Path -LiteralPath $authorProject)) { throw 'R2 authoring host is missing' }
try {
    Invoke-R2Process (Join-Path $EngineDirectory 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') @(
        "`"$authorProject`"", '-run=pythonscript', "`"-script=$r2Directory\author.py`"",
        '-unattended', '-nosplash', '-NoSound', '-NoSourceControl', '-NoZenLocalFallback',
        "`"-abslog=$r2Directory\author_ue.log`"") 'automatic_author'
    $authoring = Get-Content -LiteralPath (Join-Path $evidenceDirectory 'authoring_result.json') -Raw | ConvertFrom-Json
    if ($authoring.status -ne 'PASS') { throw "Authoring failed at $($authoring.failed_stage): $($authoring.error)" }
    Invoke-R2Process (Join-Path $EngineDirectory 'Engine\Binaries\Win64\UnrealEditor.exe') @(
        "`"$projectDirectory\MHTo3DCharacter.uproject`"", "`"-ExecutePythonScript=$r2Directory\playback.py`"",
        '-unattended', '-nosplash', '-NoSound', '-NoSourceControl', '-NoZenLocalFallback',
        '-RenderOffscreen', '-windowed', '-ResX=1920', '-ResY=1080',
        "`"-abslog=$r2Directory\playback_ue.log`"") 'automatic_playback'
} finally {
    & python (Join-Path $r2Directory 'finalise.py')
    if ($LASTEXITCODE -ne 0) { throw 'R2 finalisation failed' }
}
$final = Get-Content -LiteralPath (Join-Path $evidenceDirectory 'result.json') -Raw | ConvertFrom-Json
if ($final.status -ne 'PASS') { throw "R2 module result: $($final.status)" }
Write-Output 'R2 automatic pipeline PASS'
