$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
& 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/MHTo3DCharacter.uproject' "-Plugin=$taskRoot/NativeHost/Plugins/Phase4CTools/Phase4CTools.uplugin" '-EnablePlugins=MetaHumanCharacter,Phase4CTools' '-run=pythonscript' "-script=$taskRoot/ue_proposals.py" '-unattended' '-nosplash' '-nosound' '-NullRHI' '-NoAnalytics' '-NoAutoSave' '-ddc=InstalledNoZenLocalFallback' '-DDC-ForceMemoryCache' "-abslog=$taskRoot/proposals_ue.log" *> (Join-Path $taskRoot 'proposals_stdout.log')
if($LASTEXITCODE -ne 0){throw "Unreal proposals returned $LASTEXITCODE"}
Get-Content -LiteralPath (Join-Path $taskRoot 'proposals_stdout.log') -Tail 8
