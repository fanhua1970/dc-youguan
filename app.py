from flask import Flask, request, send_file, render_template, jsonify, after_this_request
import yt_dlp
import os
import uuid
import logging

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 配置日志，方便排查 yt-dlp 的内部问题
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt_dlp_app")

def download_audio(url, output_path):
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]',  # itag=140 或 best m4a
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [],  # 不进行任何后处理/转码
        'keepvideo': False,
        'prefer_ffmpeg': False,  # 避免依赖 ffmpeg
        # 核心：增加客户端伪装，防止 YouTube 封锁导致 extract_info 崩溃
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except yt_dlp.utils.DownloadError as de:
        logger.error(f"YouTube 下载器报错: {de}")
        return False
    except Exception as e:
        logger.error(f"下载时发生未知异常: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "请提供 YouTube URL"}), 400

        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.m4a"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        # 1. 触发下载（直接同步下载，配合前端加一个 Loading 动画是最稳妥的）
        # 如果坚持要用全异步，建议引入 Celery / Redis Queue，这种用 threading+join 的做法是反模式。
        success = download_audio(url, filepath)

        if success and os.path.exists(filepath):
            
            # 2. 关键修复：注册一个“请求完成后”的钩子，确保 Flask 把文件发送给浏览器后，再安全删除文件
            @after_this_request
            def remove_file(response):
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"成功清理临时文件: {filepath}")
                except Exception as error:
                    logger.error(f"清理临时文件失败: {error}")
                return response

            # 3. 发送文件
            return send_file(filepath, as_attachment=True, download_name=f"youtube_audio_{filename}")
        else:
            # 下载失败时，清理可能产生的残留空文件
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": "下载失败，YouTube 限制了请求或链接无效。请稍后重试或检查容器 yt-dlp 版本。"}), 500

    return render_template('index.html')

if __name__ == '__main__':
    # 生产环境请确保容器内执行了: pip install -U yt-dlp
    app.run(host='0.0.0.0', port=8080, debug=False)
