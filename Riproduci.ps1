$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Eseguire prima Avvia.ps1 per creare l’ambiente.' }
& $python -m controlled_d2t.cli synth --n 1200 --seed 42
if ($LASTEXITCODE -ne 0) { throw 'Generazione dati fallita.' }
& $python -m controlled_d2t.cli experiment --bootstrap 200
if ($LASTEXITCODE -ne 0) { throw 'Esperimento fallito.' }
& $python -m pytest
if ($LASTEXITCODE -ne 0) { throw 'Test falliti.' }
