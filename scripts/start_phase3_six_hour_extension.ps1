$ErrorActionPreference = 'Stop'
$phase3Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $phase3Root
$cpuPython = Join-Path $phase3Root 'tmp/phase3-reference-env/Scripts/python.exe'
Add-Type @'
using System.Runtime.InteropServices;
public class Phase3ExtensionPower {
    [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint flags);
}
'@
[void][Phase3ExtensionPower]::SetThreadExecutionState(2147483649)
try {
    & $cpuPython -u scripts/run_phase3_dc_eviction_extension.py
    if ($LASTEXITCODE -ne 0) { throw "Training exited with code $LASTEXITCODE. Inspect the supervisor log before resuming." }
    $env:PHASE3_EVICTION_AUDIT_OUT = 'results/phase3-dc-eviction-six-seed-v1'
    $env:PHASE3_EVICTION_ADMISSION = 'DC'
    & python -u scripts/audit_phase3_eviction_block.py
    if ($LASTEXITCODE -ne 0) { throw "Audit exited with code $LASTEXITCODE. Completed training artifacts remain available." }
    Write-Output 'DC eviction extension and paired analysis completed.'
} finally {
    [void][Phase3ExtensionPower]::SetThreadExecutionState(2147483648)
}
