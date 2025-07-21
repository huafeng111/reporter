FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区为北京时间
ENV TZ=Asia/Shanghai
RUN apt-get update && apt-get install -y \
    tzdata \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 复制项目文件
COPY . .

# 创建虚拟环境并安装依赖
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync

# 创建日志目录
RUN mkdir -p /var/log/reporter

# 复制定时任务配置
COPY deploy/crontab /etc/cron.d/reporter
RUN chmod 0644 /etc/cron.d/reporter && \
    crontab /etc/cron.d/reporter

# 创建启动脚本
RUN cat > /start.sh << 'EOF'
#!/bin/bash
# 启动 cron 服务
service cron start
# 保持容器运行
tail -f /var/log/reporter/agents.log
EOF

RUN chmod +x /start.sh

# 暴露日志目录作为数据卷
VOLUME ["/var/log/reporter"]

# 启动容器
CMD ["/start.sh"] 