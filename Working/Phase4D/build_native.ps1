$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
$taskPlugin=Join-Path $taskRoot 'NativeHost/Plugins/Phase4DTools'
$taskRsp=Join-Path $taskPlugin 'Intermediate/Build/Win64/x64/UnrealEditor/Development/Phase4DTools'
$taskVc='C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x64'
New-Item -ItemType Directory -Path (Join-Path $taskPlugin 'Binaries/Win64') -Force | Out-Null
Push-Location 'D:/Epic Games/UE_5.8/Engine/Source'
try {
 foreach($taskFile in @('Phase4DLibrary.cpp.obj.rsp','Module.Phase4DTools.cpp.obj.rsp')) {
  & (Join-Path $taskVc 'cl.exe') "@$(Join-Path $taskRsp $taskFile)"
  if($LASTEXITCODE -ne 0){throw "Compiler failed: $taskFile"}
 }
 # This editor bridge needs no executable icon/version resource.
 $taskDllRsp=Join-Path $taskRsp 'UnrealEditor-Phase4DTools.dll.rsp'
 Get-Content -LiteralPath $taskDllRsp | Where-Object {$_ -notmatch '\.res"$'} | Set-Content -LiteralPath ($taskDllRsp+'.filtered')
 & (Join-Path $taskVc 'link.exe') /LIB "@$(Join-Path $taskRsp 'UnrealEditor-Phase4DTools.lib.rsp')"
 if($LASTEXITCODE -ne 0){throw 'Library link failed'}
 & (Join-Path $taskVc 'link.exe') "@$(Join-Path $taskRsp 'UnrealEditor-Phase4DTools.dll.rsp.filtered')"
 if($LASTEXITCODE -ne 0){throw 'DLL link failed'}
 $taskBuildId=(Get-Content 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.modules' -Raw | ConvertFrom-Json).BuildId
 @{BuildId=$taskBuildId;Modules=@{Phase4DTools='UnrealEditor-Phase4DTools.dll'}} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskPlugin 'Binaries/Win64/UnrealEditor.modules') -Encoding utf8
} finally {Pop-Location}
