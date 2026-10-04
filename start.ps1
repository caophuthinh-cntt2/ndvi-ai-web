# ==========================================
# NDVI AI Web - Start Script
# Script khởi động backend và frontend
# ==========================================

$ErrorActionPreference = "Stop"

# Hàm hiển thị thông báo màu
function Write-ColorOutput($ForegroundColor, $Message) {
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Hàm kiểm tra lỗi
function Exit-OnError($Message) {
    Write-ColorOutput Red "❌ LỖI: $Message"
    Write-Host ""
    Write-Host "Nhấn phím bất kỳ để thoát..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  NDVI AI Web - Start Script"
Write-ColorOutput Cyan "=========================================="
Write-Host ""

# Lưu đường dẫn gốc
$PROJECT_ROOT = $PSScriptRoot

# ==========================================
# Kiểm tra file .env
# ==========================================
Write-ColorOutput Yellow "🔍 Kiểm tra cấu hình..."
$envFile = Join-Path $PROJECT_ROOT ".env"

if (-not (Test-Path $envFile)) {
    Exit-OnError "File .env không tồn tại. Vui lòng chạy .\setup.ps1 trước."
}
Write-ColorOutput Green "✓ File .env tồn tại"

# ==========================================
# Kiểm tra và khởi động Docker Compose
# ==========================================
Write-ColorOutput Yellow "`n🐳 Khởi động PostgreSQL..."
try {
    Set-Location $PROJECT_ROOT
    
    # Kiểm tra container đã chạy chưa
    $containerStatus = & docker ps --filter "name=ndvi-postgres" --format "{{.Status}}" 2>&1
    
    if ($containerStatus -match "Up") {
        Write-ColorOutput Green "✓ PostgreSQL đã đang chạy"
    } else {
        Write-ColorOutput Cyan "Đang khởi động Docker containers..."
        & docker-compose up -d
        
        if ($LASTEXITCODE -ne 0) {
            Exit-OnError "Không thể khởi động Docker Compose"
        }
        
        # Đợi database sẵn sàng
        Write-ColorOutput Cyan "Đợi database sẵn sàng..."
        Start-Sleep -Seconds 5
        Write-ColorOutput Green "✓ PostgreSQL đã khởi động"
    }
} catch {
    Exit-OnError "Lỗi khi khởi động Docker: $_"
}

# ==========================================
# Khởi động Backend
# ==========================================
Write-ColorOutput Yellow "`n🚀 Khởi động Backend..."
$backendPath = Join-Path $PROJECT_ROOT "backend"
$venvActivate = Join-Path $PROJECT_ROOT "backend\venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    Exit-OnError "Virtual environment không tồn tại. Vui lòng chạy .\setup.ps1 trước."
}

# Tạo script tạm để chạy backend
$backendScript = @"
Set-Location '$backendPath'
& '$venvActivate'
Write-Host 'Backend đang chạy tại http://localhost:8000' -ForegroundColor Green
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host 'Nhấn Ctrl+C để dừng' -ForegroundColor Yellow
Write-Host ''
uvicorn app.main:app --reload --port 8000
"@

$backendScriptPath = Join-Path $env:TEMP "ndvi_backend_start.ps1"
$backendScript | Out-File -FilePath $backendScriptPath -Encoding UTF8

# Khởi động backend trong window mới
Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScriptPath
Write-ColorOutput Green "✓ Backend đang khởi động..."

# ==========================================
# Khởi động Frontend
# ==========================================
Write-ColorOutput Yellow "`n🚀 Khởi động Frontend..."
$frontendPath = Join-Path $PROJECT_ROOT "frontend"

if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Exit-OnError "Node modules không tồn tại. Vui lòng chạy .\setup.ps1 trước."
}

# Tạo script tạm để chạy frontend
$frontendScript = @"
Set-Location '$frontendPath'
Write-Host 'Frontend đang chạy tại http://localhost:5173' -ForegroundColor Green
Write-Host 'Nhấn Ctrl+C để dừng' -ForegroundColor Yellow
Write-Host ''
npm run dev
"@

$frontendScriptPath = Join-Path $env:TEMP "ndvi_frontend_start.ps1"
$frontendScript | Out-File -FilePath $frontendScriptPath -Encoding UTF8

# Khởi động frontend trong window mới
Start-Process powershell -ArgumentList "-NoExit", "-File", $frontendScriptPath
Write-ColorOutput Green "✓ Frontend đang khởi động..."

# ==========================================
# Đợi services khởi động
# ==========================================
Write-ColorOutput Yellow "`n⏳ Đợi services khởi động hoàn tất..."
Start-Sleep -Seconds 5

# ==========================================
# Mở trình duyệt
# ==========================================
Write-ColorOutput Yellow "`n🌐 Mở trình duyệt..."
try {
    Start-Process "http://localhost:5173"
    Write-ColorOutput Green "✓ Đã mở trình duyệt"
} catch {
    Write-ColorOutput Yellow "⚠️  Không thể mở trình duyệt tự động. Vui lòng truy cập: http://localhost:5173"
}

# ==========================================
# Hiển thị thông tin
# ==========================================
Write-Host ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  ✅ HỆ THỐNG ĐANG CHẠY!"
Write-ColorOutput Green "=========================================="
Write-Host ""
Write-ColorOutput Cyan "📍 URLs:"
Write-Host "  Frontend:  " -NoNewline
Write-ColorOutput Yellow "http://localhost:5173"
Write-Host "  Backend:   " -NoNewline
Write-ColorOutput Yellow "http://localhost:8000"
Write-Host "  API Docs:  " -NoNewline
Write-ColorOutput Yellow "http://localhost:8000/docs"
Write-Host ""
Write-ColorOutput Cyan "🎛️  Quản lý:"
Write-Host "  - Backend và Frontend đang chạy trong các cửa sổ riêng"
Write-Host "  - Nhấn Ctrl+C trong mỗi cửa sổ để dừng service đó"
Write-Host "  - Hoặc chạy: " -NoNewline
Write-ColorOutput Yellow ".\stop.ps1" -NoNewline
Write-Host " để dừng tất cả"
Write-Host ""
Write-ColorOutput Cyan "📝 Lưu ý:"
Write-Host "  - Backend sẽ tự động reload khi code thay đổi"
Write-Host "  - Frontend sẽ tự động reload khi code thay đổi"
Write-Host "  - PostgreSQL đang chạy trong Docker container"
Write-Host ""
Write-Host "Nhấn phím bất kỳ để đóng cửa sổ này..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
