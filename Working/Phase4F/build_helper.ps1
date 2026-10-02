$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSCommandPath
$taskRsp=Join-Path $taskRoot 'NativeHost/Plugins/Phase4CTools/Intermediate/Build/Win64/x64/UnrealEditor/Development/Phase4CTools'
$taskVc='C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x64'
Push-Location 'D:/Epic Games/UE_5.8/Engine/Source'
try {
 & (Join-Path $taskVc 'cl.exe') "@$(Join-Path $taskRsp 'Phase4CLibrary.cpp.obj.rsp')"
 if($LASTEXITCODE -ne 0){throw 'Phase4F helper compile failed'}
 & (Join-Path $taskVc 'link.exe') "@$(Join-Path $taskRsp 'UnrealEditor-Phase4CTools.dll.rsp')"
 if($LASTEXITCODE -ne 0){throw 'Phase4F helper link failed'}
} finally {Pop-Location}
