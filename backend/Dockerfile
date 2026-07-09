# ============================================================
# 万语风 (PolyWind) Backend — Multi-stage Dockerfile
# ============================================================

# ── Stage 1: Builder ──
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml README.md ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: Runtime ──
FROM python:3.11-slim AS runtime

# 安全：创建非 root 用户
RUN groupadd -r polywind && useradd -r -g polywind polywind

WORKDIR /app

# 从 builder 复制已安装的包
COPY --from=builder /install /usr/local

# 复制应用代码
COPY app/ ./app/

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POLYWIND_ENV=production

# 切换到非 root 用户
USER polywind

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/health', timeout=5); r.raise_for_status()"

EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
