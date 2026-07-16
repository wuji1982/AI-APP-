# AI星木共享商城平台 - Windows部署脚本
# 使用方法: .\deploy.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI星木共享商城平台 - Windows部署脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查Docker
function Check-Docker {
    Write-Host "`n[1/5] 检查Docker环境..." -ForegroundColor Yellow
    try {
        $version = docker --version
        Write-Host "Docker已安装: $version" -ForegroundColor Green
    } catch {
        Write-Host "Docker未安装！请先安装Docker Desktop" -ForegroundColor Red
        Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
}

# 检查Docker运行状态
function Check-DockerRunning {
    Write-Host "`n[2/5] 检查Docker运行状态..." -ForegroundColor Yellow
    try {
        docker info | Out-Null
        Write-Host "Docker正在运行" -ForegroundColor Green
    } catch {
        Write-Host "Docker未运行！请启动Docker Desktop" -ForegroundColor Red
        exit 1
    }
}

# 配置环境变量
function Setup-Environment {
    Write-Host "`n[3/5] 配置环境变量..." -ForegroundColor Yellow
    if (-not (Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host ".env文件已创建" -ForegroundColor Green
        Write-Host "请编辑 .env 填入以下配置:" -ForegroundColor Yellow
        Write-Host "  - LLM_API_KEY: OpenAI API密钥"
        Write-Host "  - DIFY_API_KEY: Dify平台API密钥"
        Write-Host "  - OPENIM_SECRET: OpenIM密钥"
        $editEnv = Read-Host "是否现在编辑.env文件? (y/n)"
        if ($editEnv -eq 'y') {
            notepad .env
        }
    } else {
        Write-Host ".env文件已存在" -ForegroundColor Green
    }
}

# 启动服务
function Start-Services {
    Write-Host "`n[4/5] 启动所有服务..." -ForegroundColor Yellow
    
    # 启动基础设施
    Write-Host "  启动数据库和缓存..." -ForegroundColor Gray
    docker-compose up -d postgres redis rabbitmq minio
    
    Write-Host "  等待数据库就绪..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
    
    # 启动IM
    Write-Host "  启动即时通讯服务..." -ForegroundColor Gray
    docker-compose up -d openim-mongo openim-server
    
    # 启动Dify
    Write-Host "  启动Dify RAG平台..." -ForegroundColor Gray
    docker-compose up -d dify-api dify-web
    
    # 启动后端
    Write-Host "  启动后端服务..." -ForegroundColor Gray
    docker-compose up -d backend celery-worker celery-beat
    
    # 启动Nginx
    Write-Host "  启动Nginx..." -ForegroundColor Gray
    docker-compose up -d nginx
    
    Write-Host "所有服务启动完成!" -ForegroundColor Green
}

# 显示状态
function Show-Status {
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "  服务状态:" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    docker-compose ps
    
    Write-Host "`n==========================================" -ForegroundColor Green
    Write-Host "  服务访问地址:" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  后端API文档:  http://localhost:8000/api/docs"
    Write-Host "  Dify RAG平台: http://localhost:3800"
    Write-Host "  OpenIM API:   http://localhost:10002"
    Write-Host "  RabbitMQ管理: http://localhost:15672"
    Write-Host "  MinIO控制台:  http://localhost:9001"
    
    Write-Host "`n==========================================" -ForegroundColor Yellow
    Write-Host "  默认账号:" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "  管理员: 13800000000 / admin123"
    Write-Host "  测试用户: 13800000001 / test123"
    Write-Host ""
}

# 主流程
Check-Docker
Check-DockerRunning
Setup-Environment
Start-Services
Show-Status
