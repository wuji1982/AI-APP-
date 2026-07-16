#!/bin/bash
# AI星木共享商城平台 - 一键部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

echo "=========================================="
echo "  AI星木共享商城平台 - 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker
check_docker() {
    echo -e "${YELLOW}[1/6] 检查Docker环境...${NC}"
    if ! command -v docker &> /dev/null; then
        echo "Docker未安装，正在安装..."
        curl -fsSL https://get.docker.com | sh
        systemctl start docker
        systemctl enable docker
        echo -e "${GREEN}Docker安装完成${NC}"
    else
        echo -e "${GREEN}Docker已安装: $(docker --version)${NC}"
    fi
}

# 检查Docker Compose
check_compose() {
    echo -e "${YELLOW}[2/6] 检查Docker Compose...${NC}"
    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose未安装，正在安装..."
        pip3 install docker-compose || pip install docker-compose
        echo -e "${GREEN}Docker Compose安装完成${NC}"
    else
        echo -e "${GREEN}Docker Compose已安装${NC}"
    fi
}

# 配置环境变量
setup_env() {
    echo -e "${YELLOW}[3/6] 配置环境变量...${NC}"
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${GREEN}.env文件已创建，请编辑 .env 填入实际配置${NC}"
        echo -e "${YELLOW}  必填项:${NC}"
        echo "  - LLM_API_KEY: OpenAI API密钥"
        echo "  - DIFY_API_KEY: Dify平台API密钥"
        echo "  - OPENIM_SECRET: OpenIM密钥"
    else
        echo -e "${GREEN}.env文件已存在${NC}"
    fi
}

# 启动基础设施
start_infrastructure() {
    echo -e "${YELLOW}[4/6] 启动基础设施服务...${NC}"
    docker-compose up -d postgres redis rabbitmq minio
    echo "等待数据库就绪..."
    sleep 10
    
    # 检查PostgreSQL健康状态
    until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
        echo "等待PostgreSQL..."
        sleep 2
    done
    echo -e "${GREEN}基础设施服务启动完成${NC}"
}

# 启动IM服务
start_im() {
    echo -e "${YELLOW}[5/6] 启动即时通讯服务...${NC}"
    docker-compose up -d openim-mongo openim-server
    sleep 5
    echo -e "${GREEN}IM服务启动完成${NC}"
}

# 启动应用服务
start_application() {
    echo -e "${YELLOW}[6/6] 启动应用服务...${NC}"
    
    # 启动Dify
    docker-compose up -d dify-api dify-web
    
    # 启动后端
    docker-compose up -d backend celery-worker celery-beat
    
    # 启动Nginx
    docker-compose up -d nginx
    
    echo -e "${GREEN}应用服务启动完成${NC}"
}

# 显示服务状态
show_status() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}  部署完成！服务状态:${NC}"
    echo "=========================================="
    docker-compose ps
    echo ""
    echo "=========================================="
    echo "  服务访问地址:"
    echo "=========================================="
    echo "  前端管理后台:  http://$(hostname -I | awk '{print $1}')"
    echo "  后端API文档:  http://$(hostname -I | awk '{print $1}'):8000/api/docs"
    echo "  Dify RAG平台: http://$(hostname -I | awk '{print $1}'):3800"
    echo "  OpenIM API:   http://$(hostname -I | awk '{print $1}'):10002"
    echo "  RabbitMQ管理: http://$(hostname -I | awk '{print $1}'):15672"
    echo "  MinIO控制台:  http://$(hostname -I | awk '{print $1}'):9001"
    echo ""
    echo "=========================================="
    echo "  默认账号:"
    echo "=========================================="
    echo "  管理员: 13800000000 / admin123"
    echo "  测试用户: 13800000001 / test123"
    echo ""
}

# 执行部署
main() {
    check_docker
    check_compose
    setup_env
    start_infrastructure
    start_im
    start_application
    show_status
}

main "$@"
