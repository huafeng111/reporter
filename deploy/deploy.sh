#!/bin/bash

# 金融新闻报告器部署脚本
# 适用于 Ubuntu/Debian 系统

set -e

echo "🚀 开始部署金融新闻报告器..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="reporter"
PROJECT_DIR="/opt/${PROJECT_NAME}"
SERVICE_USER="reporter"
PYTHON_VERSION="3.11"

# 检查是否为 root 用户
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此脚本需要 root 权限运行${NC}"
   echo "请使用: sudo bash deploy.sh"
   exit 1
fi

echo -e "${YELLOW}更新系统包...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}安装必要的系统依赖...${NC}"
apt install -y python3 python3-pip python3-venv curl git cron

echo -e "${YELLOW}创建服务用户...${NC}"
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash $SERVICE_USER
    echo -e "${GREEN}已创建用户: $SERVICE_USER${NC}"
else
    echo -e "${GREEN}用户 $SERVICE_USER 已存在${NC}"
fi

echo -e "${YELLOW}安装 uv 包管理器...${NC}"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # 将 uv 添加到 PATH
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/$SERVICE_USER/.bashrc
else
    echo -e "${GREEN}uv 已安装${NC}"
fi

echo -e "${YELLOW}创建项目目录...${NC}"
mkdir -p $PROJECT_DIR
chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

echo -e "${YELLOW}复制项目文件...${NC}"
# 假设当前目录是项目根目录
cp -r . $PROJECT_DIR/
chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

echo -e "${YELLOW}切换到服务用户并设置环境...${NC}"
sudo -u $SERVICE_USER bash << EOF
cd $PROJECT_DIR

# 安装 uv（用户级别）
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="\$HOME/.local/bin:\$PATH"
fi

# 创建虚拟环境并安装依赖
~/.local/bin/uv venv
source .venv/bin/activate
~/.local/bin/uv sync

echo -e "${GREEN}Python 环境设置完成${NC}"
EOF

echo -e "${YELLOW}创建环境变量文件...${NC}"
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    echo "请输入您的 BochaAI API Key:"
    read -r BOCHAAI_API_KEY
    echo "请输入您的 DeepSeek API Key:"
    read -r DEEPSEEK_API_KEY
    echo "请输入您的 Slack Webhook URL:"
    read -r SLACK_WEBHOOK_URL
    
    cat > "$PROJECT_DIR/.env" << EOF
# BochaAI 搜索 API 配置
BOCHAAI_SEARCH_URL=https://api.bochaai.com/v1/web-search
BOCHAAI_API_KEY=$BOCHAAI_API_KEY

# DeepSeek 分析 API 配置  
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner

# Slack 配置
SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL
USE_SLACK_BLOCKS=True

# 搜索配置
DEFAULT_QUERY=总结昨天的美股金融财经新闻
FRESHNESS=day
COUNT=50
EOF
    chown $SERVICE_USER:$SERVICE_USER "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
    echo -e "${GREEN}环境变量配置完成${NC}"
else
    echo -e "${GREEN}.env 文件已存在${NC}"
fi

echo -e "${YELLOW}创建日志目录...${NC}"
mkdir -p /var/log/$PROJECT_NAME
chown $SERVICE_USER:$SERVICE_USER /var/log/$PROJECT_NAME
chmod 755 /var/log/$PROJECT_NAME

echo -e "${YELLOW}设置智能调度系统...${NC}"
# 使用项目中的 crontab 配置文件
cp "$PROJECT_DIR/deploy/crontab" /tmp/crontab_tmp

# 替换路径变量
sed -i "s|/app|$PROJECT_DIR|g" /tmp/crontab_tmp
sed -i "s|/var/log/reporter|/var/log/$PROJECT_NAME|g" /tmp/crontab_tmp

# 安装定时任务到指定用户
sudo -u $SERVICE_USER crontab /tmp/crontab_tmp
rm -f /tmp/crontab_tmp

# 验证crontab安装
echo -e "${GREEN}验证crontab安装...${NC}"
echo "当前crontab内容:"
sudo -u $SERVICE_USER crontab -l

# 手动运行一次调度器来初始化日志文件
echo -e "${YELLOW}初始化调度器日志...${NC}"
sudo -u $SERVICE_USER bash -c "cd $PROJECT_DIR && source .venv/bin/activate && python scripts/run_scheduler.py >> /var/log/$PROJECT_NAME/scheduler.log 2>&1"

echo -e "${GREEN}智能调度系统已安装${NC}"

echo -e "${YELLOW}启动 cron 服务...${NC}"
systemctl enable cron
systemctl start cron

echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}项目目录: $PROJECT_DIR${NC}"
echo -e "${GREEN}日志文件: /var/log/$PROJECT_NAME/scheduler.log${NC}"
echo -e "${GREEN}智能调度: 每分钟检查配置文件中的任务时间表${NC}"
echo ""
echo -e "${YELLOW}当前任务调度安排:${NC}"
echo "  • 8:00 - 每日美股财经新闻总结"
echo "  • 8:05 - 美股宏观经济因素分析"
echo "  • 8:10 - 每日加密货币市场新闻摘要"
echo "  • 每周一8:00 - 每周美股风险与机会分析"
echo ""
echo -e "${YELLOW}测试智能调度器:${NC}"
echo "sudo -u $SERVICE_USER bash -c 'cd $PROJECT_DIR && source .venv/bin/activate && python scripts/run_scheduler.py'"
echo ""
echo -e "${YELLOW}测试单个配置文件:${NC}"
echo "sudo -u $SERVICE_USER bash -c 'cd $PROJECT_DIR && source .venv/bin/activate && python scripts/run_agents.py --config config/crypto_tasks.yaml'"
echo ""
echo -e "${YELLOW}查看调度日志:${NC}"
echo "tail -f /var/log/$PROJECT_NAME/scheduler.log"
echo ""
echo -e "${YELLOW}查看定时任务:${NC}"
echo "crontab -u $SERVICE_USER -l" 