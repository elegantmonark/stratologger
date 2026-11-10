# Generate the Stratologger SL-1 bare-board fabrication package.
# Author: Trishan Biswas
# Project started: February 2026
# Status: Ongoing

param(
    [string]$KiCadCli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$boardPath = Join-Path $scriptRoot "Stratologger_SL1.kicad_pcb"
$manufacturingPath = Join-Path $scriptRoot "manufacturing"
$gerberPath = Join-Path $manufacturingPath "gerbers"
$drcPath = Join-Path $manufacturingPath "Stratologger_SL1-drc.rpt"
$positionPath = Join-Path $manufacturingPath "Stratologger_SL1-top-pos.csv"
$zipPath = Join-Path $manufacturingPath "Stratologger_SL1-fabrication.zip"

if (-not (Test-Path -LiteralPath $KiCadCli)) {
    throw "KiCad CLI was not found at: $KiCadCli"
}

$releasePath = Join-Path $scriptRoot "release-status.json"
if (-not (Test-Path -LiteralPath $releasePath)) {
    throw "Fabrication blocked: missing release-status.json."
}
$release = Get-Content -Raw -LiteralPath $releasePath | ConvertFrom-Json
if ($release.fabrication_approved -ne $true) {
    throw "Fabrication blocked: $($release.status). $($release.reason)"
}

if (Test-Path -LiteralPath $gerberPath) {
    # Resolve and check this narrow generated directory before recursive removal.
    $resolvedRoot = (Resolve-Path -LiteralPath $scriptRoot).Path
    $resolvedGerbers = (Resolve-Path -LiteralPath $gerberPath).Path
    if ($resolvedGerbers -ne (Join-Path $resolvedRoot "manufacturing\gerbers")) {
        throw "Refusing to remove an unexpected Gerber directory: $resolvedGerbers"
    }
    Remove-Item -LiteralPath $gerberPath -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $gerberPath | Out-Null

& $KiCadCli pcb drc --refill-zones --exit-code-violations `
    --output $drcPath --units mm $boardPath
if ($LASTEXITCODE -ne 0) {
    throw "KiCad DRC failed. Read $drcPath before generating manufacturing data."
}

& $KiCadCli pcb export gerbers --check-zones --precision 6 `
    --layers "F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts" `
    --output $gerberPath $boardPath
if ($LASTEXITCODE -ne 0) {
    throw "Gerber export failed."
}

& $KiCadCli pcb export drill --format excellon --excellon-units mm `
    --excellon-separate-th `
    --generate-report --report-path (Join-Path $manufacturingPath "Stratologger_SL1-drill.rpt") `
    --output $gerberPath $boardPath
if ($LASTEXITCODE -ne 0) {
    throw "Drill export failed."
}

& $KiCadCli pcb export pos --side front --format csv --units mm --smd-only `
    --output $positionPath $boardPath
if ($LASTEXITCODE -ne 0) {
    throw "Position export failed."
}

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -Path (Join-Path $gerberPath "*") -DestinationPath $zipPath

Write-Output "DRC report: $drcPath"
Write-Output "Fabrication ZIP: $zipPath"
