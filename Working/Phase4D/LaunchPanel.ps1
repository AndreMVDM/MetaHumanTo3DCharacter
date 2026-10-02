$phase4dRoot = $PSScriptRoot
$phase4dPythonw = 'C:\Users\Andre\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe'
if (-not (Test-Path -LiteralPath $phase4dPythonw)) { throw 'Bundled Python runtime unavailable; locate a working Python 3.11 Tcl/Tk installation before launching.' }
Start-Process -FilePath $phase4dPythonw -ArgumentList @((Join-Path $phase4dRoot 'panel.py')) -WorkingDirectory $phase4dRoot -WindowStyle Hidden
