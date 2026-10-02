$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'APoseDDC') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'APoseShaders') -Force | Out-Null
[Environment]::SetEnvironmentVariable('UE-LocalDataCachePath',(Join-Path $taskRoot 'APoseDDC'),'Process')
$taskArguments=@('"E:/Repo/UE/Projects/MetaHumanTo3DCharacter/MHTo3DCharacter.uproject"','/Game/MetaHumanTo3DCharacter/Phase4F/John/Maps/L_JohnReview','-NoSplash','-NoSound','-NoAutoSave','-NoAnalytics','-ddc=InstalledNoZenLocalFallback',"-LocalDataCachePath=`"$taskRoot/APoseDDC`"", "-ShaderWorkingDir=`"$taskRoot/APoseShaders`"", "-abslog=`"$taskRoot/apose_editor_review.log`"",'-ExecCmds="py E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4F/apose_open_review.py"')
$taskEditor=Start-Process -FilePath 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArguments -WindowStyle Normal -PassThru
@{process_id=$taskEditor.Id;log='Working/Phase4F/apose_editor_review.log';purpose='Interactive human A-pose review; zero approvals during startup'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'apose_review_editor_process.json') -Encoding utf8
$taskEditor.Id
