$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
Add-Type @'
using System.Runtime.InteropServices;
public class Phase3Power { [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint flags); }
'@
[void][Phase3Power]::SetThreadExecutionState(2147483649)
try {
    & "$taskRoot/tmp/phase3-reference-env/Scripts/python.exe" -u "$PSScriptRoot/run_phase3_overnight.py" --hours 7.5
    $trainingExit = $LASTEXITCODE
    if ($trainingExit -ne 0) { Write-Output "Training stopped with exit code $trainingExit; preserving all committed results." }
    & 'C:/Python314/python.exe' "$PSScriptRoot/finalize_phase3_overnight.py"
    if ($LASTEXITCODE -ne 0) { throw 'Finalization failed; see error log.' }
} finally {
    [void][Phase3Power]::SetThreadExecutionState(2147483648)
}
