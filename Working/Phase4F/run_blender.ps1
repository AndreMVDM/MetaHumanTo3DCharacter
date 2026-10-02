$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --factory-startup -b --python-exit-code 1 --python (Join-Path $taskRoot 'prepare_sources.py') *> (Join-Path $taskRoot 'prepare_sources.log')
if($LASTEXITCODE -ne 0){throw "Blender returned $LASTEXITCODE"}
Get-Content -LiteralPath (Join-Path $taskRoot 'prepare_sources.log') -Tail 5
