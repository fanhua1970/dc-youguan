FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 在 Dockerfile 中更新
RUN pip install -U yt-dlp

COPY . .

# 创建下载目录
RUN mkdir -p downloads

EXPOSE 8080

CMD ["python", "app.py"]
