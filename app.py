from flask import Flask, request, send_file, render_template, jsonify
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_audio(url, output_path):
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]',  # itag=140 或 best m4a
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [],  # 关键：不进行任何后处理/转码
        'keepvideo': False,
        'prefer_ffmpeg': False,  # 避免 ffmpeg
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "请提供 YouTube URL"}), 400

        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.m4a"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        try:
            # 异步下载（避免阻塞）
            thread = threading.Thread(target=download_audio, args=(url, filepath))
            thread.start()
            thread.join(timeout=120)  # 最多等2分钟

            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
            else:
                return jsonify({"error": "下载失败或超时"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            # 清理文件（可选，节省空间）
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
