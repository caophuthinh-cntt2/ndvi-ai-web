# ==========================================
# NDVI AI Web - Reset Database Script
# Script reset database (cho development)
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
Write-ColorOutput Cyan "  NDVI AI Web - Reset Database"
Write-ColorOutput Cyan "=========================================="
Write-Host ""

# Cảnh báo
Write-ColorOutput Red "⚠️  CẢNH BÁO: Script này sẽ XÓA TẤT CẢ DỮ LIỆU trong database!"
Write-Host ""
Write-ColorOutput Yellow "Bạn có chắc chắn muốn tiếp tục? (y/N): " -NoNewline
$confirm = Read-Host

if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-ColorOutput Yellow "Đã hủy bỏ."
    Start-Sleep -Seconds 1
    exit 0
}

Write-Host ""
Write-ColorOutput Yellow "Nhập 'RESET' để xác nhận: " -NoNewline
$confirmReset = Read-Host

if ($confirmReset -ne "RESET") {
    Write-ColorOutput Yellow "Đã hủy bỏ."
    Start-Sleep -Seconds 1
    exit 0
}

Write-Host ""

# Lưu đường dẫn gốc
$PROJECT_ROOT = $PSScriptRoot

# ==========================================
# BƯỚC 1: Dừng các services đang chạy
# ==========================================
Write-ColorOutput Yellow "🛑 Bước 1: Dừng các services..."

# Dừng Backend
try {
    $backendProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
                        Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($backendProcesses) {
        foreach ($pid in $backendProcesses) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
        Write-ColorOutput Green "✓ Đã dừng Backend"
    }
} catch {
    # Bỏ qua nếu không chạy
}

# Dừng Frontend
try {
    $frontendProcesses = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | 
                         Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($frontendProcesses) {
        foreach ($pid in $frontendProcesses) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
        Write-ColorOutput Green "✓ Đã dừng Frontend"
    }
} catch {
    # Bỏ qua nếu không chạy
}

Start-Sleep -Seconds 2

# ==========================================
# BƯỚC 2: Kiểm tra Docker
# ==========================================
Write-ColorOutput Yellow "`n🐳 Bước 2: Kiểm tra Docker..."
try {
    $dockerPs = & docker ps 2>&1
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Docker Desktop không chạy. Vui lòng khởi động Docker Desktop."
    }
    Write-ColorOutput Green "✓ Docker đang chạy"
} catch {
    Exit-OnError "Không thể kết nối Docker"
}

# ==========================================
# BƯỚC 3: Load environment variables
# ==========================================
Write-ColorOutput Yellow "`n⚙️  Bước 3: Load cấu hình..."
$envFile = Join-Path $PROJECT_ROOT ".env"

if (-not (Test-Path $envFile)) {
    Exit-OnError "File .env không tồn tại"
}

# Parse .env file
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

$dbName = if ($envVars.ContainsKey("POSTGRES_DB")) { $envVars["POSTGRES_DB"] } else { "ndvi_db" }
$dbUser = if ($envVars.ContainsKey("POSTGRES_USER")) { $envVars["POSTGRES_USER"] } else { "postgres" }

Write-ColorOutput Green "✓ Database: $dbName"
Write-ColorOutput Green "✓ User: $dbUser"

# ==========================================
# BƯỚC 4: Dừng Docker container
# ==========================================
Write-ColorOutput Yellow "`n🛑 Bước 4: Dừng Docker container..."
try {
    Set-Location $PROJECT_ROOT
    & docker-compose down
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Không thể dừng Docker Compose"
    }
    
    Write-ColorOutput Green "✓ Đã dừng Docker container"
    Start-Sleep -Seconds 2
} catch {
    Exit-OnError "Lỗi khi dừng Docker: $_"
}

# ==========================================
# BƯỚC 5: Xóa Docker volume (optional)
# ==========================================
Write-ColorOutput Yellow "`n🗑️  Bước 5: Xóa Docker volume..."
try {
    $volumeName = "ndvi-ai-web_postgres_data"
    $volumeExists = & docker volume ls --format "{{.Name}}" | Select-String -Pattern $volumeName
    
    if ($volumeExists) {
        & docker volume rm $volumeName 2>&1 | Out-Null
        Write-ColorOutput Green "✓ Đã xóa Docker volume"
    } else {
        Write-ColorOutput Gray "  Volume không tồn tại, bỏ qua"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Không thể xóa volume, tiếp tục..."
}

# ==========================================
# BƯỚC 6: Khởi động lại Docker container
# ==========================================
Write-ColorOutput Yellow "`n🐳 Bước 6: Khởi động Docker container..."
try {
    Set-Location $PROJECT_ROOT
    & docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Không thể khởi động Docker Compose"
    }
    
    Write-ColorOutput Green "✓ Docker container đã khởi động"
} catch {
    Exit-OnError "Lỗi khi khởi động Docker: $_"
}

# ==========================================
# BƯỚC 7: Đợi PostgreSQL sẵn sàng
# ==========================================
Write-ColorOutput Yellow "`n⏳ Bước 7: Đợi PostgreSQL sẵn sàng..."
Write-ColorOutput Cyan "Đang đợi (tối đa 30 giây)..."

$maxAttempts = 30
$attempt = 0
$dbReady = $false

while ($attempt -lt $maxAttempts -and -not $dbReady) {
    Start-Sleep -Seconds 1
    $attempt++
    
    try {
        $testConnection = & docker exec ndvi-postgres pg_isready -U postgres 2>&1
        if ($testConnection -match "accepting connections") {
            $dbReady = $true
            Write-ColorOutput Green "✓ PostgreSQL đã sẵn sàng"
        }
    } catch {
        # Tiếp tục đợi
    }
    
    if (-not $dbReady -and $attempt -lt $maxAttempts) {
        Write-Host "." -NoNewline
    }
}

if (-not $dbReady) {
    Exit-OnError "PostgreSQL không khởi động được sau 30 giây"
}

# ==========================================
# BƯỚC 8: Khởi tạo database
# ==========================================
Write-ColorOutput Yellow "`n🗄️  Bước 8: Khởi tạo database..."
try {
    Set-Location $PROJECT_ROOT
    
    # Activate virtual environment
    $venvActivate = Join-Path $PROJECT_ROOT "backend\venv\Scripts\Activate.ps1"
    if (-not (Test-Path $venvActivate)) {
        Exit-OnError "Virtual environment không tồn tại. Chạy setup.ps1 trước."
    }
    
    & $venvActivate
    
    Write-ColorOutput Cyan "Chạy setup_database.py..."
    & python scripts/setup_database.py
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Khởi tạo database thất bại"
    }
    
    Write-ColorOutput Green "✓ Đã khởi tạo database"
} catch {
    Exit-OnError "Lỗi khi khởi tạo database: $_"
}

# ==========================================
# BƯỚC 9: Nạp dữ liệu mẫu
# ==========================================
Write-ColorOutput Yellow "`n📊 Bước 9: Nạp dữ liệu mẫu..."
try {
    Write-ColorOutput Cyan "Chạy ingest_all.py (có thể mất vài phút)..."
    & python scripts/ingest_all.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Yellow "⚠️  Nạp dữ liệu có lỗi, nhưng database đã reset"
    } else {
        Write-ColorOutput Green "✓ Đã nạp dữ liệu mẫu"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Lỗi khi nạp dữ liệu: $_, nhưng database đã reset"
}

# ==========================================
# Hoàn tất
# ==========================================
Write-Host ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  ✅ RESET DATABASE HOÀN TẤT!"
Write-ColorOutput Green "=========================================="
Write-Host ""
Write-ColorOutput Cyan "📋 Các bước tiếp theo:"
Write-Host "  - Chạy: " -NoNewline
Write-ColorOutput Yellow ".\start.ps1" -NoNewline
Write-Host " để khởi động hệ thống"
Write-Host "  - Database đã được reset về trạng thái ban đầu"
Write-Host "  - Dữ liệu cũ đã bị xóa hoàn toàn"
Write-Host ""
Write-Host "Nhấn phím bất kỳ để thoát..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
