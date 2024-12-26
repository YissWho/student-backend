# 使用 Python 3.11.9 基础镜像
FROM python:3.11.9

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目依赖文件
COPY requirements.txt .

# 安装项目依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件到容器中
COPY . .

# 暴露端口 8001
EXPOSE 8001

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]