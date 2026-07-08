# ══════════════════════════════════════════════
#  构建阶段
# ══════════════════════════════════════════════
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# 换阿里云APT源 + 删除有问题的docker-clean脚本
RUN set -e; \
    rm -f /etc/apt/sources.list.d/debian.sources; \
    echo 'deb [trusted=yes] http://mirrors.aliyun.com/debian bookworm main' > /etc/apt/sources.list; \
    echo 'deb [trusted=yes] http://mirrors.aliyun.com/debian bookworm-updates main' >> /etc/apt/sources.list; \
    echo 'deb [trusted=yes] http://mirrors.aliyun.com/debian-security bookworm-security main' >> /etc/apt/sources.list; \
    rm -f /etc/apt/apt.conf.d/docker-clean

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 限制编译并发，降低内存峰值
ENV MAX_JOBS=1
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# ══════════════════════════════════════════════
#  运行阶段
# ══════════════════════════════════════════════
FROM python:3.11-slim-bookworm

WORKDIR /app

# 换阿里云APT源
RUN set -e; \
    rm -f /etc/apt/sources.list.d/debian.sources; \
    echo 'deb [trusted=yes] http://mirrors.aliyun.com/debian bookworm main' > /etc/apt/sources.list; \
    echo 'deb [trusted=yes] http://mirrors.aliyun.com/debian bookworm-updates main' >> /etc/apt/sources.list; \
    echo 'deb [trusted=yes] http://mirrors.aliyun.com/debian-security bookworm-security main' >> /etc/apt/sources.list; \
    rm -f /etc/apt/apt.conf.d/docker-clean

# 运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    wget \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/uploads /app/data/vector_db /app/data/inverted_index

# 环境变量
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:5000/api/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "run:app"]
