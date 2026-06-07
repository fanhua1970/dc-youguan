from flask import Flask, request, send_file, render_template, jsonify, after_this_request
import yt_dlp
import os
import uuid
import logging

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt_dlp_app")

# =====================================================================
# 🎯 核心改动 1：直接把 cookies.txt 的全部内容粘贴到这里（死写进代码）
# 注意：前后的三个单引号 ''' 不要删掉，直接把内容贴在它们中间。
# =====================================================================
COOKIES_TEXT = # Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1796414089	__Secure-YNID	19.YT=enAstUrSDOWCGbnYv_okl3wn4JcWSAsYN0-2rHnpClo9n7nJErWe4PI-C-odSshZgFbiS9dLYL-wfNeKTMroJp12btJ-uQoeN46qIikmSMaE96j211u3Pcp6IBHylMauwGCiTSK4wCim6RmYcXeKPIJxOWyEE8CosURKqIukNnCyMgBC4mNMoAE0NbQrv072XacJNUSTpH1jxhZS7IPUHUJrWbdtTK3lfBYvfn_Yu4OC8bfU5jsEf2KUXoj5GNboCXLjq_5288pD7ZMUIs0NearJINc67eclQy5TNGND2MAifAF9d-qtHKyz6tFYt5oXFdn9g1M751hIUmgUlbemGg
.youtube.com	TRUE	/	TRUE	1780293773	GPS	1
.youtube.com	TRUE	/	TRUE	1796414092	VISITOR_INFO1_LIVE	ysbw7_O3MmQ
.youtube.com	TRUE	/	TRUE	1796414092	VISITOR_PRIVACY_METADATA	CgJDQRIEGgAgOA%3D%3D
.youtube.com	TRUE	/	TRUE	1815422096	PREF	tz=America.Vancouver&f5=30000
.youtube.com	TRUE	/	TRUE	1812398098	__Secure-1PSIDTS	sidts-CjUByojQUzU1We71wfE8V4DBZ1MQBgx-RZg5XKR0kr_kNJwOx35S57W_9eorusyIMzWXzPgBnRAA
.youtube.com	TRUE	/	TRUE	1812398098	__Secure-3PSIDTS	sidts-CjUByojQUzU1We71wfE8V4DBZ1MQBgx-RZg5XKR0kr_kNJwOx35S57W_9eorusyIMzWXzPgBnRAA
.youtube.com	TRUE	/	FALSE	1814852056	HSID	AHBQaR6abx_dez1nR
.youtube.com	TRUE	/	TRUE	1814852056	SSID	AR2uQO356Ytbr1ou9
.youtube.com	TRUE	/	FALSE	1814852056	APISID	_6zAvfMS5yRG5DmU/A8lltiz8k6yEA5Lj7
.youtube.com	TRUE	/	TRUE	1814852056	SAPISID	8eJsnbaqBFrz4lXx/AU6BoE_06U0DadwyK
.youtube.com	TRUE	/	TRUE	1814852056	__Secure-1PAPISID	8eJsnbaqBFrz4lXx/AU6BoE_06U0DadwyK
.youtube.com	TRUE	/	TRUE	1814852056	__Secure-3PAPISID	8eJsnbaqBFrz4lXx/AU6BoE_06U0DadwyK
.youtube.com	TRUE	/	FALSE	1814852056	SID	g.a000-giqpcXDPKeZMfctBKt99JLkhFPXRDzXcEZW5EeoFmDn9f4KdsSfjUvAZ_fo6kZYxstoLQACgYKAVkSARYSFQHGX2MigLWPxBMDVB4j7rcIvBD7mBoVAUF8yKpJ1KLNOj77InV-52TigFpB0076
.youtube.com	TRUE	/	TRUE	1814852056	__Secure-1PSID	g.a000-giqpcXDPKeZMfctBKt99JLkhFPXRDzXcEZW5EeoFmDn9f4KOf3qceWttNqSBecg81zSTwACgYKAV4SARYSFQHGX2MiUbSsKZOyxEeOeMMZALM3FhoVAUF8yKqVjJEHrhEGLeM0Mz14m6sc0076
.youtube.com	TRUE	/	TRUE	1814852056	__Secure-3PSID	g.a000-giqpcXDPKeZMfctBKt99JLkhFPXRDzXcEZW5EeoFmDn9f4Kd8ssVhA7XItscM83kugxlwACgYKATASARYSFQHGX2MingXxG9lSL1LywdWrKbChjhoVAUF8yKoPoNZvw6-nC8cGJ2cJhci10076
.youtube.com	TRUE	/	TRUE	1814852056	LOGIN_INFO	AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H:QUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3
.youtube.com	TRUE	/	FALSE	1812398107	SIDCC	AKEyXzVp_G0inP7g1aA7aoNK74vBkV3y1z1eqtZXLV3BoR7UrKFneOqgImnldCi2II5D6jdqtw
.youtube.com	TRUE	/	TRUE	1812398107	__Secure-1PSIDCC	AKEyXzX9rbINwi_ZnPDgHbWDy9F3PC3962HA6z_pd5HXkfGQDJ4BJsR9hhwP5_BmlK0Eqqa4
.youtube.com	TRUE	/	TRUE	1812398107	__Secure-3PSIDCC	AKEyXzU2BVhk4ISAHeXTu_bT4rQ_ZJ9U9vxWu5dnyxXnD1zop8BFaOlcN_LLofKLqPG47nht
.youtube.com	TRUE	/	FALSE	1780292065	ST-l3hjtt	session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3
.youtube.com	TRUE	/	FALSE	1780292082	ST-b55704	itct=CP8CENwwIhMIsMvz3KjllAMVNg9oCB2v9ig7MgZnLWhpZ2haD0ZFd2hhdF90b193YXRjaJoBBhCOHhiACsoBBIf5vUU%3D&csn=fB62euV3_nU3So4c&session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3&endpoint=%7B%22clickTrackingParams%22%3A%22CP8CENwwIhMIsMvz3KjllAMVNg9oCB2v9ig7MgZnLWhpZ2haD0ZFd2hhdF90b193YXRjaJoBBhCOHhiACsoBBIf5vUU%3D%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fwatch%3Fv%3DJWKqoYj8Npg%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_WATCH%22%2C%22rootVe%22%3A3832%7D%7D%2C%22watchEndpoint%22%3A%7B%22videoId%22%3A%22JWKqoYj8Npg%22%2C%22watchEndpointSupportedOnesieConfig%22%3A%7B%22html5PlaybackOnesieConfig%22%3A%7B%22commonConfig%22%3A%7B%22url%22%3A%22https%3A%2F%2Frr1---sn-uxa0n-t8gd.googlevideo.com%2Finitplayback%3Fsource%3Dyoutube%26oeis%3D1%26c%3DWEB%26oad%3D3200%26ovd%3D3200%26oaad%3D11000%26oavd%3D11000%26ocs%3D700%26oewis%3D1%26oputc%3D1%26ofpcc%3D1%26siu%3D1%26msp%3D1%26odepv%3D1%26id%3D2562aaa188fc3698%26ip%3D2001%253A569%253A50fb%253A6d00%253Ada3a%253Addff%253Afed1%253Abdd0%26initcwndbps%3D3892500%26mt%3D1780291746%26oweuc%3D%26pxtags%3DCg4KAnR4Egg1MTgyODk2OA%26rxtags%3DCg4KAnR4Egg1MTgyODk2Nw%252CCg4KAnR4Egg1MTgyODk2OA%22%7D%7D%7D%7D%7D
.youtube.com	TRUE	/	TRUE	0	YSC	8RH12eb-VZk
.youtube.com	TRUE	/	FALSE	1780862099	ST-tladcw	session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3
.youtube.com	TRUE	/	FALSE	1780862099	ST-3opvp5	session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3
.youtube.com	TRUE	/	FALSE	1780862101	ST-xuwub9	session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3
.youtube.com	TRUE	/	FALSE	1780862104	ST-ywt1sz	itct=CIgEENwwIhMIs_LWofT1lAMVIgnWAB1U7hqzMgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngHKAQSH-b1F&csn=u1CBm94Q6_gsNVme&session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3&endpoint=%7B%22clickTrackingParams%22%3A%22CIgEENwwIhMIs_LWofT1lAMVIgnWAB1U7hqzMgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngHKAQSH-b1F%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fwatch%3Fv%3DP9rmhRnDbLw%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_WATCH%22%2C%22rootVe%22%3A3832%7D%7D%2C%22watchEndpoint%22%3A%7B%22videoId%22%3A%22P9rmhRnDbLw%22%2C%22watchEndpointSupportedOnesieConfig%22%3A%7B%22html5PlaybackOnesieConfig%22%3A%7B%22commonConfig%22%3A%7B%22url%22%3A%22https%3A%2F%2Frr2---sn-uxa0n-t8gr.googlevideo.com%2Finitplayback%3Fsource%3Dyoutube%26oeis%3D1%26c%3DWEB%26oad%3D3200%26ovd%3D3200%26oaad%3D11000%26oavd%3D11000%26ocs%3D700%26oewis%3D1%26oputc%3D1%26ofpcc%3D1%26siu%3D1%26msp%3D1%26odepv%3D1%26id%3D3fdae68519c36cbc%26ip%3D2001%253A569%253A50fb%253A6d00%253Ada3a%253Addff%253Afed1%253Abdd0%26initcwndbps%3D3395000%26mt%3D1780861762%26oweuc%3D%22%7D%7D%7D%7D%7D
.youtube.com	TRUE	/	FALSE	1780862112	ST-amrb2j	session_logininfo=AFmmF2swRAIgKnKdZy0IihWLiVgvkgN43LY9oLgokP7ixiDfx79E1ckCIE-hG4JBi4KHgEESm2qp9y3medBhoXKdlY2e0FsR8e4H%3AQUQ3MjNmeUFyXzFWOG9hb2dYcDBpY0VVb3VRWWQ4ZEpHQzRjQ1lXVlNwY3dGcVlPYkxmaUppb1hGMWVHTmlrbWhCT3doS3FMRWZLS0hPb2tBdFFLSTEtSlBiQ3FMcExfSWdNR0UxcndlbXZwMS1xRmpuRTQyZWgtLW9qMFdMV25VMjFUVjg2Q1FUNGFJbVNNWGtDdWN4cjFzbTM5SE9vSTZ3
.youtube.com	TRUE	/	TRUE	1796414089	__Secure-ROLLOUT_TOKEN	COfH6eSi0PqwUxDCro61qOWUAxiVwNGh9PWUAw%3D%3D
 
'''
# Netscape HTTP Cookie File
# http://curl.haxx.se/docs/http-cookies.html
# This file was generated by yt-dlp

.youtube.com	TRUE	/	TRUE	1798112345	__Secure-3PAPISID	xxxxxxxxx
.youtube.com	TRUE	/	TRUE	1798112345	__Secure-3PSID	xxxxxxxxx
(把你的 cookies.txt 里面的全部文字完整粘贴替换到这里...)
'''

# 自动在运行目录生成一个真实的物理文件
COOKIES_FILE_PATH = os.path.abspath("temp_cookies.txt")
with open(COOKIES_FILE_PATH, "w", encoding="utf-8") as f:
    f.write(COOKIES_TEXT.strip())

def download_audio(url, output_path):
    ydl_opts = {
        'format': '140/bestaudio[ext=m4a]',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [],
        'keepvideo': False,
        'prefer_ffmpeg': False,
        
        # 🎯 核心改动 2：强制指向这个在容器里刚生成的本地 Cookies 文件
        'cookiefile': COOKIES_FILE_PATH,
        
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    
    # 🎯 核心改动 3：内部全面捕获，绝不让异常抛出到外部线程
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, "成功"
    except Exception as e:
        logger.error(f"yt-dlp 内部下载失败: {e}")
        return False, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "请提供 YouTube URL"}), 400

        # 生成随机唯一文件名
        filename = f"{uuid.uuid4().hex}.m4a"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        # 🎯 核心改动 4：这里没有任何 threading.Thread！完全由当前 Flask 请求链同步执行！
        success, err_msg = download_audio(url, filepath)

        if success and os.path.exists(filepath):
            @after_this_request
            def remove_file(response):
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"清理文件成功: {filepath}")
                except Exception as e:
                    logger.error(f"清理文件失败: {e}")
                return response

            return send_file(filepath, as_attachment=True, download_name=f"audio_{filename}")
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"下载失败，原因: {err_msg}"}), 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
