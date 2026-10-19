$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Installare Python 3.11 o successivo e riprovare.' }
    & $python -m pip install -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Installazione dipendenze non riuscita.' }
    & $python -m pip install -e '.[test]'
    if ($LASTEXITCODE -ne 0) { throw 'Installazione progetto non riuscita.' }
}
& $python -m streamlit run app.py --server.address 127.0.0.1
