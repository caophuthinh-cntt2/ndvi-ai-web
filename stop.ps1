# ==========================================
# NDVI AI Web - Stop Script
# Script dừng tất cả services
# ==========================================

$ErrorActionPreference = "Continue"

# Hàm hiển thị thông báo màu
function Write-ColorOutput($ForegroundColor, $Message) {
    Write-Host $Message -ForegroundColor $ForegroundColor
}

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  NDVI AI Web - Stop Script"
Write-ColorOutput Cyan "=========================================="
Write-Host ""

# Lưu đường dẫn gốc
$PROJECT_ROOT = $PSScriptRoot

# ==========================================
# Dừng Backend (port 8000)
# ==========================================
Write-ColorOutput Yellow "🛑 Dừng Backend..."
try {
    $backendProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
                        Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($backendProcesses) {
        foreach ($pid in $backendProcesses) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-ColorOutput Green "✓ Đã dừng Backend (PID: $pid)"
                }
            } catch {
                # Bỏ qua lỗi
            }
        }
    } else {
        Write-ColorOutput Gray "  Backend không chạy hoặc không dùng port 8000"
    }
} catch {
    Write-ColorOutput Gray "  Không tìm thấy Backend đang chạy"
}

# ==========================================
# Dừng Frontend (port 5173)
# ==========================================
Write-ColorOutput Yellow "`n🛑 Dừng Frontend..."
try {
    $frontendProcesses = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | 
                         Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($frontendProcesses) {
        foreach ($pid in $frontendProcesses) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-ColorOutput Green "✓ Đã dừng Frontend (PID: $pid)"
                }
            } catch {
                # Bỏ qua lỗi
            }
        }
    } else {
        Write-ColorOutput Gray "  Frontend không chạy hoặc không dùng port 5173"
    }
} catch {
    Write-ColorOutput Gray "  Không tìm thấy Frontend đang chạy"
}

# ==========================================
# Dừng Docker Compose
# ==========================================
Write-ColorOutput Yellow "`n🐳 Dừng Docker Compose..."
try {
    Set-Location $PROJECT_ROOT
    
    # Kiểm tra container có đang chạy không
    $containerRunning = & docker ps --filter "name=ndvi-postgres" --format "{{.Names}}" 2>&1
    
    if ($containerRunning -match "ndvi-postgres") {
        Write-ColorOutput Cyan "Đang dừng Docker containers..."
        & docker-compose down
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "✓ Đã dừng Docker containers"
        } else {
            Write-ColorOutput Yellow "⚠️  Dừng Docker containers có lỗi"
        }
    } else {
        Write-ColorOutput Gray "  Docker containers không chạy"
    }
} catch {
    Write-ColorOutput Gray "  Không thể dừng Docker containers: $_"
}

# ==========================================
# Dọn dẹp các PowerShell windows
# ==========================================
Write-ColorOutput Yellow "`n🧹 Dọn dẹp các process còn sót..."
try {
    # Tìm và dừng các process uvicorn
    $uvicornProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*" }
    foreach ($proc in $uvicornProcesses) {
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Write-ColorOutput Green "✓ Đã dừng uvicorn process (PID: $($proc.Id))"
        } catch {
            # Bỏ qua lỗi
        }
    }
    
    # Tìm và dừng các process node (vite)
    $viteProcesses = Get-Process | Where-Object { $_.ProcessName -eq "node" }
    foreach ($proc in $viteProcesses) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -like "*vite*" -or $cmdLine -like "*npm*dev*") {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                Write-ColorOutput Green "✓ Đã dừng node/vite process (PID: $($proc.Id))"
            }
        } catch {
            # Bỏ qua lỗi
        }
    }
} catch {
    # Bỏ qua lỗi dọn dẹp
}

# ==========================================
# Hoàn tất
# ==========================================
Write-Host ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  ✅ ĐÃ DỪNG TẤT CẢ SERVICES"
Write-ColorOutput Green "=========================================="
Write-Host ""
Write-ColorOutput Cyan "📋 Để khởi động lại:"
Write-Host "  Chạy: " -NoNewline
Write-ColorOutput Yellow ".\start.ps1"
Write-Host ""
Write-Host "Nhấn phím bất kỳ để thoát..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
