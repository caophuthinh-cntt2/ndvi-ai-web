$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot

Write-Host "Starting NDVI backend on http://localhost:8000" -ForegroundColor Green
$backend = Start-Process python -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory (Join-Path $projectRoot "backend") -PassThru

Write-Host "Starting NDVI frontend on http://localhost:5173" -ForegroundColor Green
$frontend = Start-Process npm.cmd -ArgumentList "run","dev","--","--host","127.0.0.1" -WorkingDirectory (Join-Path $projectRoot "frontend") -PassThru

Write-Host "Backend PID: $($backend.Id); Frontend PID: $($frontend.Id)" -ForegroundColor Cyan
Write-Host "Stop the processes when finished." -ForegroundColor Yellow
