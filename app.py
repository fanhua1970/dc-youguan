from flask import Flask, request, send_file, render_template, jsonify, after_this_request
import yt_dlp
import os
import uuid
import logging

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 开启标准日志，方便在云平台控制台查看真实下载错误
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt_dlp_app")

# 🎯 动态从环境变量恢复 cookies 文件的绝对路径
COOKIES_PATH = os.path.join(os.path.abspath(DOWNLOAD_FOLDER), 'cookies.txt')
cookies_env = os.environ.get('YT_COOKIES_DATA')

if cookies_env:
    try:
        with open(COOKIES_PATH, 'w', encoding='utf-8') as f:
            f.write(cookies_env.strip())
        logger.info(f"成功从环境变量加载 YouTube Cookies，写入路径: {COOKIES_PATH}")
    except Exception as e:
        logger.error(f"写入 Cookies 文件失败: {e}")
else:
    logger.warning("未检测到 YT_COOKIES_DATA 环境变量，将尝试免登录下载（极易被封锁）")

def download_audio(url, output_path):
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]',  # itag=140 或 best m4a
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [],  # 不进行任何后处理
        'keepvideo': False,
        'prefer_ffmpeg': False,  # 避免依赖 ffmpeg
        
        # 🎯 关键：如果存在从环境变量生成的 cookies 文件，就直接引用它
        'cookiefile': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        
        # 增加移动端客户端欺骗
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    
    # 🎯 核心修复：在下载函数内部进行全包裹捕获，确保不扩散到线程层
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, "成功"
    except yt_dlp.utils.DownloadError as de:
        error_msg = str(de)
        logger.error(f"yt-dlp 下载器拦截报错: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = str(e)
        logger.error(f"下载时发生未知异常: {error_msg}")
        return False, error_msg

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "请提供 YouTube URL"}), 400

        # 生成唯一种子文件名
        filename = f"{uuid.uuid4().hex}.m4a"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        # 🎯 核心修复：移除你原本代码中的 threading.Thread，改为直接同步调用
        # 这样 Flask 可以直接捕获到成功或失败的状态
        success, message = download_audio(url, filepath)

        if success and os.path.exists(filepath):
            
            # 注册钩子：等 Flask 把文件完全传输给用户浏览器后，再执行删除
            @after_this_request
            def remove_file(response):
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"临时音频文件清理成功: {filepath}")
                except Exception as error:
                    logger.error(f"清理临时文件失败: {error}")
                return response

            return send_file(filepath, as_attachment=True, download_name=f"download_{filename}")
        else:
            # 下载失败时的清理与友好提示
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # 友好提示：如果是机器人拦截，直接给前端具体原因
            friendly_err = "下载失败。YouTube 限制了请求（提示需要验证机器人）。请检查云平台环境变量中的 Cookies 是否过期。" if "bot" in message.lower() else f"下载失败: {message}"
            return jsonify({"error": friendly_err}), 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
