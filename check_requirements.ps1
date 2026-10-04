# ==========================================
# NDVI AI Web - Check Requirements Script
# Script kiểm tra môi trường hệ thống
# ==========================================

$ErrorActionPreference = "Continue"

# Hàm hiển thị thông báo màu
function Write-ColorOutput($ForegroundColor, $Message) {
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Biến đếm lỗi
$errorCount = 0
$warningCount = 0

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  NDVI AI Web - Kiểm tra Môi trường"
Write-ColorOutput Cyan "=========================================="
Write-Host ""

# Lưu đường dẫn gốc
$PROJECT_ROOT = $PSScriptRoot

# ==========================================
# 1. Kiểm tra Python
# ==========================================
Write-ColorOutput Yellow "🔍 1. Kiểm tra Python..."
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3]
        
        if ($major -ge 3 -and $minor -ge 11) {
            Write-ColorOutput Green "   ✓ Python: $pythonVersion"
        } else {
            Write-ColorOutput Red "   ✗ Python version quá thấp: $pythonVersion (cần >= 3.11)"
            $errorCount++
        }
    } else {
        Write-ColorOutput Red "   ✗ Không thể xác định Python version"
        $errorCount++
    }
} catch {
    Write-ColorOutput Red "   ✗ Python không được cài đặt"
    $errorCount++
}

# Kiểm tra pip
try {
    $pipVersion = & pip --version 2>&1
    if ($pipVersion -match "pip") {
        Write-ColorOutput Green "   ✓ pip: Đã cài đặt"
    }
} catch {
    Write-ColorOutput Yellow "   ⚠ pip không tìm thấy"
    $warningCount++
}

# ==========================================
# 2. Kiểm tra Node.js
# ==========================================
Write-ColorOutput Yellow "`n🔍 2. Kiểm tra Node.js..."
try {
    $nodeVersion = & node --version 2>&1
    if ($nodeVersion -match "v(\d+)\.(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        
        if ($major -ge 18) {
            Write-ColorOutput Green "   ✓ Node.js: $nodeVersion"
        } else {
            Write-ColorOutput Red "   ✗ Node.js version quá thấp: $nodeVersion (cần >= 18)"
            $errorCount++
        }
    }
} catch {
    Write-ColorOutput Red "   ✗ Node.js không được cài đặt"
    $errorCount++
}

# Kiểm tra npm
try {
    $npmVersion = & npm --version 2>&1
    Write-ColorOutput Green "   ✓ npm: v$npmVersion"
} catch {
    Write-ColorOutput Yellow "   ⚠ npm không tìm thấy"
    $warningCount++
}

# ==========================================
# 3. Kiểm tra Docker
# ==========================================
Write-ColorOutput Yellow "`n🔍 3. Kiểm tra Docker..."
try {
    $dockerVersion = & docker --version 2>&1
    if ($dockerVersion -match "Docker version") {
        Write-ColorOutput Green "   ✓ Docker: $dockerVersion"
        
        # Kiểm tra Docker daemon
        $dockerPs = & docker ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "   ✓ Docker daemon: Đang chạy"
        } else {
            Write-ColorOutput Red "   ✗ Docker daemon: Không chạy"
            $errorCount++
        }
    }
} catch {
    Write-ColorOutput Red "   ✗ Docker không được cài đặt"
    $errorCount++
}

# Kiểm tra docker-compose
try {
    $composeVersion = & docker-compose --version 2>&1
    if ($composeVersion -match "version") {
        Write-ColorOutput Green "   ✓ Docker Compose: $composeVersion"
    }
} catch {
    Write-ColorOutput Yellow "   ⚠ Docker Compose không tìm thấy"
    $warningCount++
}

# ==========================================
# 4. Kiểm tra Project Structure
# ==========================================
Write-ColorOutput Yellow "`n🔍 4. Kiểm tra Project Structure..."

$requiredFolders = @(
    "backend",
    "frontend",
    "scripts",
    "data"
)

foreach ($folder in $requiredFolders) {
    $folderPath = Join-Path $PROJECT_ROOT $folder
    if (Test-Path $folderPath) {
        Write-ColorOutput Green "   ✓ Thư mục $folder: Tồn tại"
    } else {
        Write-ColorOutput Red "   ✗ Thư mục $folder: Không tồn tại"
        $errorCount++
    }
}

# ==========================================
# 5. Kiểm tra Python Virtual Environment
# ==========================================
Write-ColorOutput Yellow "`n🔍 5. Kiểm tra Python Virtual Environment..."
$venvPath = Join-Path $PROJECT_ROOT "backend\venv"

if (Test-Path $venvPath) {
    Write-ColorOutput Green "   ✓ Virtual environment: Tồn tại"
    
    # Kiểm tra activate script
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-ColorOutput Green "   ✓ Activate script: Tồn tại"
    } else {
        Write-ColorOutput Red "   ✗ Activate script: Không tồn tại"
        $errorCount++
    }
} else {
    Write-ColorOutput Red "   ✗ Virtual environment: Không tồn tại (chạy setup.ps1)"
    $errorCount++
}

# ==========================================
# 6. Kiểm tra Dependencies
# ==========================================
Write-ColorOutput Yellow "`n🔍 6. Kiểm tra Dependencies..."

# Python packages
if (Test-Path (Join-Path $PROJECT_ROOT "backend\requirements.txt")) {
    Write-ColorOutput Green "   ✓ requirements.txt: Tồn tại"
} else {
    Write-ColorOutput Red "   ✗ requirements.txt: Không tồn tại"
    $errorCount++
}

# Node modules
$nodeModulesPath = Join-Path $PROJECT_ROOT "frontend\node_modules"
if (Test-Path $nodeModulesPath) {
    Write-ColorOutput Green "   ✓ node_modules: Đã cài đặt"
} else {
    Write-ColorOutput Red "   ✗ node_modules: Chưa cài đặt (chạy setup.ps1)"
    $errorCount++
}

# ==========================================
# 7. Kiểm tra Configuration Files
# ==========================================
Write-ColorOutput Yellow "`n🔍 7. Kiểm tra Configuration Files..."

$envFile = Join-Path $PROJECT_ROOT ".env"
if (Test-Path $envFile) {
    Write-ColorOutput Green "   ✓ .env: Tồn tại"
    
    # Kiểm tra nội dung .env
    $envContent = Get-Content $envFile -Raw
    $requiredVars = @("DATABASE_URL", "POSTGRES_USER", "POSTGRES_PASSWORD")
    
    foreach ($var in $requiredVars) {
        if ($envContent -match $var) {
            Write-ColorOutput Green "   ✓ $var: Đã cấu hình"
        } else {
            Write-ColorOutput Yellow "   ⚠ $var: Chưa cấu hình"
            $warningCount++
        }
    }
} else {
    Write-ColorOutput Red "   ✗ .env: Không tồn tại (chạy setup.ps1)"
    $errorCount++
}

$dockerComposeFile = Join-Path $PROJECT_ROOT "docker-compose.yml"
if (Test-Path $dockerComposeFile) {
    Write-ColorOutput Green "   ✓ docker-compose.yml: Tồn tại"
} else {
    Write-ColorOutput Red "   ✗ docker-compose.yml: Không tồn tại"
    $errorCount++
}

# ==========================================
# 8. Kiểm tra PostgreSQL Connection
# ==========================================
Write-ColorOutput Yellow "`n🔍 8. Kiểm tra PostgreSQL..."

try {
    $containerStatus = & docker ps --filter "name=ndvi-postgres" --format "{{.Status}}" 2>&1
    
    if ($containerStatus -match "Up") {
        Write-ColorOutput Green "   ✓ PostgreSQL container: Đang chạy"
        
        # Test connection
        try {
            $pgReady = & docker exec ndvi-postgres pg_isready -U postgres 2>&1
            if ($pgReady -match "accepting connections") {
                Write-ColorOutput Green "   ✓ PostgreSQL connection: OK"
            } else {
                Write-ColorOutput Yellow "   ⚠ PostgreSQL: Chưa sẵn sàng"
                $warningCount++
            }
        } catch {
            Write-ColorOutput Yellow "   ⚠ Không thể kiểm tra PostgreSQL connection"
            $warningCount++
        }
    } else {
        Write-ColorOutput Yellow "   ⚠ PostgreSQL container: Không chạy"
        $warningCount++
    }
} catch {
    Write-ColorOutput Yellow "   ⚠ PostgreSQL: Không chạy (chạy start.ps1)"
    $warningCount++
}

# ==========================================
# 9. Kiểm tra Running Services
# ==========================================
Write-ColorOutput Yellow "`n🔍 9. Kiểm tra Running Services..."

# Backend
try {
    $backendPort = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($backendPort) {
        Write-ColorOutput Green "   ✓ Backend: Đang chạy (port 8000)"
    } else {
        Write-ColorOutput Gray "   ○ Backend: Không chạy"
    }
} catch {
    Write-ColorOutput Gray "   ○ Backend: Không chạy"
}

# Frontend
try {
    $frontendPort = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
    if ($frontendPort) {
        Write-ColorOutput Green "   ✓ Frontend: Đang chạy (port 5173)"
    } else {
        Write-ColorOutput Gray "   ○ Frontend: Không chạy"
    }
} catch {
    Write-ColorOutput Gray "   ○ Frontend: Không chạy"
}

# ==========================================
# Tổng kết
# ==========================================
Write-Host ""
Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  KẾT QUẢ KIỂM TRA"
Write-ColorOutput Cyan "=========================================="
Write-Host ""

if ($errorCount -eq 0 -and $warningCount -eq 0) {
    Write-ColorOutput Green "✅ Tất cả kiểm tra đều PASS!"
    Write-Host ""
    Write-ColorOutput Cyan "Hệ thống sẵn sàng. Chạy .\start.ps1 để khởi động."
} elseif ($errorCount -eq 0) {
    Write-ColorOutput Yellow "⚠️  Có $warningCount cảnh báo"
    Write-Host ""
    Write-ColorOutput Cyan "Hệ thống có thể chạy được, nhưng nên kiểm tra các cảnh báo."
} else {
    Write-ColorOutput Red "❌ Có $errorCount lỗi và $warningCount cảnh báo"
    Write-Host ""
    Write-ColorOutput Yellow "Vui lòng sửa các lỗi trước khi tiếp tục."
    Write-ColorOutput Cyan "Chạy .\setup.ps1 để cài đặt hệ thống."
}

Write-Host ""
Write-Host "Nhấn phím bất kỳ để thoát..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
