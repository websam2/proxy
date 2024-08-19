from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import re
import logging

app = Flask(__name__)
CORS(app)

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)?(www\.)?'
        r'([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-z]{2,}'
        r'(/.*)?$'
    )
    return re.match(regex, url) is not None

@app.route('/proxy_download', methods=['POST'])
def proxy_download():
    data = request.get_json()

    if not data or 'video_url' not in data or 'quality' not in data:
        return jsonify({'success': False, 'error': 'Invalid input'}), 400

    video_url = data['video_url']
    quality = data['quality']

    if not is_valid_url(video_url):
        return jsonify({'success': False, 'error': 'Invalid video URL'}), 400

    valid_qualities = ['audio', '360', '480', '720', '1080']
    if quality not in valid_qualities:
        return jsonify({'success': False, 'error': 'Invalid quality parameter'}), 400

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best' if quality != 'audio' else 'bestaudio/best',
        'extract_audio': quality == 'audio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if quality == 'audio' else [],
        'noplaylist': True,  # Evita baixar playlists inteiras
        'quiet': True,  # Reduz a verbosidade do output
        'outtmpl': '/tmp/%(title)s.%(ext)s',  # Define um diretório temporário para armazenar o arquivo
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url', None)
            title = info.get('title', None)

        return jsonify({
            'success': True,
            'download_url': download_url,
            'title': title
        })
    except yt_dlp.utils.DownloadError as e:
        logging.error(f'Download error: {e}')
        return jsonify({'success': False, 'error': 'Failed to download video'}), 500
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

