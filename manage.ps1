# AI星木共享商城平台 - 服务管理脚本
# 使用方法: .\manage.ps1 -action start|stop|restart|status|logs

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs', 'init-db')]
    [string]$action,
    
    [string]$service = ""
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI星木共享商城 - 服务管理" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

switch ($action) {
    'start' {
        if ($service) {
            Write-Host "启动服务: $service" -ForegroundColor Green
            docker-compose up -d $service
        } else {
            Write-Host "启动所有服务..." -ForegroundColor Green
            docker-compose up -d
        }
    }
    
    'stop' {
        if ($service) {
            Write-Host "停止服务: $service" -ForegroundColor Yellow
            docker-compose stop $service
        } else {
            Write-Host "停止所有服务..." -ForegroundColor Yellow
            docker-compose stop
        }
    }
    
    'restart' {
        if ($service) {
            Write-Host "重启服务: $service" -ForegroundColor Yellow
            docker-compose restart $service
        } else {
            Write-Host "重启所有服务..." -ForegroundColor Yellow
            docker-compose restart
        }
    }
    
    'status' {
        Write-Host "`n服务状态:" -ForegroundColor Cyan
        docker-compose ps
    }
    
    'logs' {
        if ($service) {
            Write-Host "查看 $service 日志..." -ForegroundColor Cyan
            docker-compose logs -f $service
        } else {
            Write-Host "查看所有服务日志..." -ForegroundColor Cyan
            docker-compose logs -f
        }
    }
    
    'init-db' {
        Write-Host "初始化数据库..." -ForegroundColor Yellow
        docker-compose exec backend python -m app.init_db
        Write-Host "数据库初始化完成!" -ForegroundColor Green
    }
}
