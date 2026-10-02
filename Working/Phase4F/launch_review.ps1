$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'DDC') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'Shaders') -Force | Out-Null
[Environment]::SetEnvironmentVariable('UE-LocalDataCachePath',(Join-Path $taskRoot 'DDC'),'Process')
$taskArguments=@('"E:/Repo/UE/Projects/MetaHumanTo3DCharacter/MHTo3DCharacter.uproject"','-NoSplash','-NoSound','-NoAutoSave','-NoAnalytics','-ddc=InstalledNoZenLocalFallback',"-LocalDataCachePath=`"$taskRoot/DDC`"", "-ShaderWorkingDir=`"$taskRoot/Shaders`"", "-abslog=`"$taskRoot/editor_review.log`"",'-ExecCmds="py E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4F/open_review.py"')
$taskEditor=Start-Process -FilePath 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArguments -WindowStyle Normal -PassThru
@{process_id=$taskEditor.Id;log='Working/Phase4F/editor_review.log';purpose='Visible interactive human review; zero anatomical approval during startup'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'review_editor_process.json') -Encoding utf8
$taskEditor.Id
