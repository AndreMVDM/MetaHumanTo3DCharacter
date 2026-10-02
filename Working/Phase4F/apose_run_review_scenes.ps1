$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'APoseDDC') -Force | Out-Null
[Environment]::SetEnvironmentVariable('UE-LocalDataCachePath',(Join-Path $taskRoot 'APoseDDC'),'Process')
& 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/MHTo3DCharacter.uproject' '-run=pythonscript' "-script=$taskRoot/apose_ue_review.py" '-unattended' '-nosplash' '-nosound' '-NullRHI' '-NoAnalytics' '-NoAutoSave' '-ddc=InstalledNoZenLocalFallback' '-DDC-ForceMemoryCache' "-abslog=$taskRoot/apose_review_scenes_ue.log" *> (Join-Path $taskRoot 'apose_review_scenes_stdout.log')
if($LASTEXITCODE -ne 0){throw "A-pose scene creation returned $LASTEXITCODE"}
& 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/MHTo3DCharacter.uproject' '-run=pythonscript' "-script=$taskRoot/apose_ue_verify_reviews.py" '-unattended' '-nosplash' '-nosound' '-NullRHI' '-NoAnalytics' '-NoAutoSave' '-ddc=InstalledNoZenLocalFallback' '-DDC-ForceMemoryCache' "-abslog=$taskRoot/apose_review_readback_ue.log" *> (Join-Path $taskRoot 'apose_review_readback_stdout.log')
if($LASTEXITCODE -ne 0){throw "A-pose readback returned $LASTEXITCODE"}
