#!/bin/bash

# 金融新闻报告器更新脚本
# 用于更新已部署的应用代码

set -e

echo "🔄 开始更新金融新闻报告器..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="financial-reporter"
PROJECT_DIR="/opt/${PROJECT_NAME}"
SERVICE_USER="reporter"

# 检查是否为 root 用户
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此脚本需要 root 权限运行${NC}"
   echo "请使用: sudo bash deploy/update.sh"
   exit 1
fi

# 检查项目目录是否存在
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo -e "${RED}错误: 项目目录 $PROJECT_DIR 不存在${NC}"
    echo -e "${YELLOW}请先运行初次部署: sudo bash deploy/deploy.sh${NC}"
    exit 1
fi

# 检查服务用户是否存在
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${RED}错误: 用户 $SERVICE_USER 不存在${NC}"
    echo -e "${YELLOW}请先运行初次部署: sudo bash deploy/deploy.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}备份当前版本...${NC}"
sudo -u $SERVICE_USER cp -r $PROJECT_DIR ${PROJECT_DIR}.backup.$(date +%Y%m%d_%H%M%S)

echo -e "${YELLOW}拉取最新代码...${NC}"
cd $PROJECT_DIR
sudo -u $SERVICE_USER git pull

echo -e "${YELLOW}更新依赖包...${NC}"
sudo -u $SERVICE_USER bash -c 'source .venv/bin/activate && ~/.local/bin/uv sync'

echo -e "${YELLOW}测试运行...${NC}"
if sudo -u $SERVICE_USER bash -c 'source .venv/bin/activate && python scripts/run_agents.py --validate'; then
    echo -e "${GREEN}✅ 更新成功！${NC}"
    echo -e "${GREEN}应用已更新到最新版本${NC}"
    
    # 清理备份（保留最近3个）
    echo -e "${YELLOW}清理旧备份...${NC}"
    ls -dt ${PROJECT_DIR}.backup.* | tail -n +4 | xargs rm -rf 2>/dev/null || true
    
else
    echo -e "${RED}❌ 测试运行失败！${NC}"
    echo -e "${YELLOW}正在回滚到备份版本...${NC}"
    
    # 找到最新的备份
    LATEST_BACKUP=$(ls -dt ${PROJECT_DIR}.backup.* 2>/dev/null | head -n 1)
    if [[ -n "$LATEST_BACKUP" ]]; then
        rm -rf $PROJECT_DIR
        mv "$LATEST_BACKUP" $PROJECT_DIR
        chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
        echo -e "${GREEN}已回滚到备份版本${NC}"
    else
        echo -e "${RED}未找到备份，请手动检查${NC}"
    fi
    exit 1
fi

echo -e "${GREEN}定时任务状态:${NC}"
if crontab -u $SERVICE_USER -l 2>/dev/null | grep -q "financial-reporter"; then
    echo -e "${GREEN}✅ 定时任务正常运行${NC}"
else
    echo -e "${YELLOW}⚠️  定时任务可能需要重新设置${NC}"
fi

echo ""
echo -e "${GREEN}🎉 更新完成！${NC}"
echo -e "${YELLOW}查看日志: tail -f /var/log/$PROJECT_NAME/daily.log${NC}"
echo -e "${YELLOW}查看定时任务: crontab -u $SERVICE_USER -l${NC}" 