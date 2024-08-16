from flask import Flask, request, jsonify
import yt_dlp
import requests
import os

app = Flask(__name__)

@app.route('/proxy_download', methods=['POST'])
def proxy_download():
    video_url = request.json['video_url']
    quality = request.json['quality']

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'extract_audio': quality == 'audio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if quality == 'audio' else [],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info['url']
            title = info['title']

        return jsonify({
            'success': True,
            'download_url': download_url,
            'title': title
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))