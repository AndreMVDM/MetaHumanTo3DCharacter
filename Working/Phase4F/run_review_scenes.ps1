$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
& 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/MHTo3DCharacter.uproject' '-run=pythonscript' "-script=$taskRoot/ue_review.py" '-unattended' '-nosplash' '-nosound' '-NullRHI' '-NoAnalytics' '-NoAutoSave' '-ddc=InstalledNoZenLocalFallback' '-DDC-ForceMemoryCache' "-abslog=$taskRoot/review_scenes_ue.log" *> (Join-Path $taskRoot 'review_scenes_stdout.log')
if($LASTEXITCODE -ne 0){throw "Unreal review scene creation returned $LASTEXITCODE"}
Get-Content -LiteralPath (Join-Path $taskRoot 'review_scenes_stdout.log') -Tail 5
