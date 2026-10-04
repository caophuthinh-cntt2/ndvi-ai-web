# ==========================================
# NDVI AI Web - Setup Script
# Script cài đặt và khởi tạo hệ thống
# ==========================================

$ErrorActionPreference = "Stop"

# Hàm hiển thị thông báo màu
function Write-ColorOutput($ForegroundColor, $Message) {
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Hàm kiểm tra lỗi và thoát
function Exit-OnError($Message) {
    Write-ColorOutput Red "❌ LỖI: $Message"
    Write-Host ""
    Write-Host "Nhấn phím bất kỳ để thoát..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  NDVI AI Web - Setup Script"
Write-ColorOutput Cyan "=========================================="
Write-Host ""

# Lưu đường dẫn gốc
$PROJECT_ROOT = $PSScriptRoot

# ==========================================
# BƯỚC 1: Kiểm tra Python
# ==========================================
Write-ColorOutput Yellow "🔍 Bước 1: Kiểm tra Python..."
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Exit-OnError "Python version phải >= 3.11. Hiện tại: $pythonVersion"
        }
        Write-ColorOutput Green "✓ Python đã cài đặt: $pythonVersion"
    }
} catch {
    Exit-OnError "Python không được cài đặt. Vui lòng cài Python 3.11+ từ https://www.python.org/"
}

# ==========================================
# BƯỚC 2: Kiểm tra Node.js
# ==========================================
Write-ColorOutput Yellow "`n🔍 Bước 2: Kiểm tra Node.js..."
try {
    $nodeVersion = & node --version 2>&1
    if ($nodeVersion -match "v(\d+)\.") {
        $major = [int]$matches[1]
        if ($major -lt 18) {
            Exit-OnError "Node.js version phải >= 18. Hiện tại: $nodeVersion"
        }
        Write-ColorOutput Green "✓ Node.js đã cài đặt: $nodeVersion"
    }
} catch {
    Exit-OnError "Node.js không được cài đặt. Vui lòng cài Node.js 18+ từ https://nodejs.org/"
}

# ==========================================
# BƯỚC 3: Kiểm tra Docker Desktop
# ==========================================
Write-ColorOutput Yellow "`n🔍 Bước 3: Kiểm tra Docker Desktop..."
try {
    $dockerVersion = & docker --version 2>&1
    if ($dockerVersion -match "Docker version") {
        Write-ColorOutput Green "✓ Docker đã cài đặt: $dockerVersion"
        
        # Kiểm tra Docker daemon có chạy không
        $dockerPs = & docker ps 2>&1
        if ($LASTEXITCODE -ne 0) {
            Exit-OnError "Docker Desktop không chạy. Vui lòng khởi động Docker Desktop và thử lại."
        }
        Write-ColorOutput Green "✓ Docker daemon đang chạy"
    }
} catch {
    Exit-OnError "Docker không được cài đặt. Vui lòng cài Docker Desktop từ https://www.docker.com/products/docker-desktop"
}

# ==========================================
# BƯỚC 4: Tạo Python Virtual Environment
# ==========================================
Write-ColorOutput Yellow "`n🔧 Bước 4: Tạo Python virtual environment..."
$venvPath = Join-Path $PROJECT_ROOT "backend\venv"

if (Test-Path $venvPath) {
    Write-ColorOutput Green "✓ Virtual environment đã tồn tại"
} else {
    try {
        Set-Location (Join-Path $PROJECT_ROOT "backend")
        & python -m venv venv
        Write-ColorOutput Green "✓ Đã tạo virtual environment"
    } catch {
        Exit-OnError "Không thể tạo virtual environment: $_"
    }
}

# ==========================================
# BƯỚC 5: Cài đặt Python packages
# ==========================================
Write-ColorOutput Yellow "`n📦 Bước 5: Cài đặt Python packages..."
try {
    Set-Location (Join-Path $PROJECT_ROOT "backend")
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Exit-OnError "Không tìm thấy activate script: $activateScript"
    }
    
    & $activateScript
    Write-ColorOutput Cyan "Đang cài đặt packages (có thể mất vài phút)..."
    & pip install --upgrade pip
    & pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Cài đặt Python packages thất bại"
    }
    
    Write-ColorOutput Green "✓ Đã cài đặt Python packages"
} catch {
    Exit-OnError "Lỗi khi cài đặt Python packages: $_"
}

# ==========================================
# BƯỚC 6: Cài đặt Node packages
# ==========================================
Write-ColorOutput Yellow "`n📦 Bước 6: Cài đặt Node packages..."
try {
    Set-Location (Join-Path $PROJECT_ROOT "frontend")
    Write-ColorOutput Cyan "Đang cài đặt packages (có thể mất vài phút)..."
    & npm install
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Cài đặt Node packages thất bại"
    }
    
    Write-ColorOutput Green "✓ Đã cài đặt Node packages"
} catch {
    Exit-OnError "Lỗi khi cài đặt Node packages: $_"
}

# ==========================================
# BƯỚC 7: Cấu hình .env file
# ==========================================
Write-ColorOutput Yellow "`n⚙️  Bước 7: Cấu hình .env file..."
Set-Location $PROJECT_ROOT

$envFile = Join-Path $PROJECT_ROOT ".env"
$envExample = Join-Path $PROJECT_ROOT ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-ColorOutput Yellow "⚠️  Đã tạo .env file từ .env.example"
        Write-ColorOutput Yellow "⚠️  VUI LÒNG CẬP NHẬT CẤU HÌNH TRONG FILE .env TRƯỚC KHI TIẾP TỤC!"
        Write-Host ""
        Write-Host "Nhấn phím bất kỳ sau khi đã cập nhật .env..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Exit-OnError "Không tìm thấy file .env.example"
    }
} else {
    Write-ColorOutput Green "✓ File .env đã tồn tại"
}

# ==========================================
# BƯỚC 8: Khởi động Docker Compose (PostgreSQL)
# ==========================================
Write-ColorOutput Yellow "`n🐳 Bước 8: Khởi động PostgreSQL với Docker Compose..."
try {
    Set-Location $PROJECT_ROOT
    Write-ColorOutput Cyan "Đang khởi động Docker containers..."
    & docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Không thể khởi động Docker Compose"
    }
    
    Write-ColorOutput Green "✓ Docker containers đang chạy"
} catch {
    Exit-OnError "Lỗi khi khởi động Docker Compose: $_"
}

# ==========================================
# BƯỚC 9: Đợi database sẵn sàng
# ==========================================
Write-ColorOutput Yellow "`n⏳ Bước 9: Đợi PostgreSQL sẵn sàng..."
Write-ColorOutput Cyan "Đang đợi database khởi động (tối đa 30 giây)..."

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
# BƯỚC 10: Khởi tạo database
# ==========================================
Write-ColorOutput Yellow "`n🗄️  Bước 10: Khởi tạo database..."
try {
    Set-Location $PROJECT_ROOT
    $activateScript = Join-Path $PROJECT_ROOT "backend\venv\Scripts\Activate.ps1"
    & $activateScript
    
    Write-ColorOutput Cyan "Đang chạy setup_database.py..."
    & python scripts/setup_database.py
    
    if ($LASTEXITCODE -ne 0) {
        Exit-OnError "Khởi tạo database thất bại"
    }
    
    Write-ColorOutput Green "✓ Đã khởi tạo database"
} catch {
    Exit-OnError "Lỗi khi khởi tạo database: $_"
}

# ==========================================
# BƯỚC 11: Nạp dữ liệu mẫu
# ==========================================
Write-ColorOutput Yellow "`n📊 Bước 11: Nạp dữ liệu mẫu..."
try {
    Write-ColorOutput Cyan "Đang chạy ingest_all.py (có thể mất vài phút)..."
    & python scripts/ingest_all.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Yellow "⚠️  Nạp dữ liệu có lỗi, nhưng tiếp tục..."
    } else {
        Write-ColorOutput Green "✓ Đã nạp dữ liệu mẫu"
    }
} catch {
    Write-ColorOutput Yellow "⚠️  Lỗi khi nạp dữ liệu: $_, nhưng tiếp tục..."
}

# ==========================================
# HOÀN TẤT
# ==========================================
Write-Host ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  ✅ CÀI ĐẶT HOÀN TẤT!"
Write-ColorOutput Green "=========================================="
Write-Host ""
Write-ColorOutput Cyan "📋 Các bước tiếp theo:"
Write-Host "  1. Chạy: " -NoNewline
Write-ColorOutput Yellow ".\start.ps1" -NoNewline
Write-Host " để khởi động hệ thống"
Write-Host "  2. Mở trình duyệt: " -NoNewline
Write-ColorOutput Yellow "http://localhost:5173"
Write-Host "  3. Backend API: " -NoNewline
Write-ColorOutput Yellow "http://localhost:8000"
Write-Host "  4. API Docs: " -NoNewline
Write-ColorOutput Yellow "http://localhost:8000/docs"
Write-Host ""
Write-ColorOutput Cyan "📚 Scripts khác:"
Write-Host "  - " -NoNewline
Write-ColorOutput Yellow ".\stop.ps1" -NoNewline
Write-Host " - Dừng tất cả services"
Write-Host "  - " -NoNewline
Write-ColorOutput Yellow ".\check_requirements.ps1" -NoNewline
Write-Host " - Kiểm tra môi trường"
Write-Host "  - " -NoNewline
Write-ColorOutput Yellow ".\reset_database.ps1" -NoNewline
Write-Host " - Reset database (development)"
Write-Host ""
Write-Host "Nhấn phím bất kỳ để thoát..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
