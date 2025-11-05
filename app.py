from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import threading
import json
import mimetypes

app = Flask(__name__)

# Dossiers de stockage
DOWNLOAD_FOLDER = 'downloads'
TEMP_FOLDER = 'temp'
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)
Path(TEMP_FOLDER).mkdir(exist_ok=True)

# Dictionnaire pour suivre l'état des téléchargements
downloads_status = {}

# Plateformes supportées
SUPPORTED_PLATFORMS = {
    'youtube': ['youtube.com', 'youtu.be', 'yt.be'],
    'vimeo': ['vimeo.com'],
    'dailymotion': ['dailymotion.com', 'dai.ly'],
    'twitter': ['twitter.com', 'x.com', 't.co'],
    'tiktok': ['tiktok.com', 'vm.tiktok.com'],
    'instagram': ['instagram.com', 'instagr.am'],
    'facebook': ['facebook.com', 'fb.watch'],
    'reddit': ['reddit.com'],
    'twitch': ['twitch.tv'],
    'soundcloud': ['soundcloud.com'],
    'spotify': ['spotify.com'],
    'generic': ['any url']
}

def detect_platform(url):
    """Détecte la plateforme vidéo"""
    url_lower = url.lower()
    for platform, domains in SUPPORTED_PLATFORMS.items():
        for domain in domains:
            if domain in url_lower:
                return platform
    return 'generic'

def progress_hook(d, download_id):
    """Fonction appelée pour suivre la progression du téléchargement"""
    if d['status'] == 'downloading':
        try:
            percent = d['_percent_str'].strip()
            speed = d['_speed_str'].strip()
            eta = d['_eta_str'].strip()
            downloads_status[download_id] = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta
            }
        except:
            pass
    elif d['status'] == 'finished':
        downloads_status[download_id] = {
            'status': 'processing',
            'message': 'Conversion en MP3...'
        }

def download_and_convert(url, download_id, output_format='mp3', quality='192'):
    """Télécharge la vidéo/audio et la convertit au format demandé"""
    try:
        platform = detect_platform(url)
        downloads_status[download_id] = {
            'status': 'starting',
            'message': f'Initialisation ({platform})...',
            'platform': platform
        }
        
        # Configuration selon le format de sortie
        postprocessors = []
        
        if output_format == 'mp3':
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }]
        elif output_format == 'wav':
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': quality,
            }]
        elif output_format == 'm4a':
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': quality,
            }]
        elif output_format == 'flac':
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
                'preferredquality': quality,
            }]
        elif output_format == 'opus':
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': quality,
            }]
        elif output_format == 'vorbis':
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
                'preferredquality': quality,
            }]
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': postprocessors,
            'outtmpl': os.path.join(TEMP_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # Configuration spéciale pour certaines plateformes
        if 'instagram' in platform or 'tiktok' in platform:
            ydl_opts['http_headers']['Referer'] = url
        
        if 'spotify' in platform:
            downloads_status[download_id] = {
                'status': 'error',
                'error': 'Spotify nécessite une authentification. Veuillez utiliser une autre source.'
            }
            return
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base_name = os.path.splitext(filename)[0]
            output_file = base_name + '.' + output_format
            
            # Déplacer le fichier vers le dossier de téléchargement
            if os.path.exists(output_file):
                final_path = os.path.join(DOWNLOAD_FOLDER, os.path.basename(output_file))
                os.rename(output_file, final_path)
                
                downloads_status[download_id] = {
                    'status': 'completed',
                    'filename': os.path.basename(final_path),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'platform': platform,
                    'format': output_format
                }
            else:
                raise Exception(f"Le fichier {output_format} n'a pas pu être créé")
    
    except Exception as e:
        downloads_status[download_id] = {
            'status': 'error',
            'error': str(e),
            'platform': platform if 'platform' in locals() else 'unknown'
        }

@app.route('/')
def index():
    """Page d'accueil avec l'interface HTML"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Endpoint pour lancer un téléchargement"""
    data = request.json
    url = data.get('url', '').strip()
    output_format = data.get('format', 'mp3').lower()
    quality = data.get('quality', '192')
    
    if not url:
        return jsonify({'error': 'URL vide'}), 400
    
    # Valider le format
    valid_formats = ['mp3', 'wav', 'm4a', 'flac', 'opus', 'vorbis']
    if output_format not in valid_formats:
        return jsonify({'error': f'Format invalide. Formats supportés: {", ".join(valid_formats)}'}), 400
    
    # Générer un ID unique pour ce téléchargement
    download_id = str(len(downloads_status))
    downloads_status[download_id] = {'status': 'queued'}
    
    # Lancer le téléchargement dans un thread séparé
    thread = threading.Thread(
        target=download_and_convert,
        args=(url, download_id, output_format, quality)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'download_id': download_id})

@app.route('/platforms', methods=['GET'])
def get_platforms():
    """Retourne les plateformes supportées"""
    return jsonify({
        'platforms': list(SUPPORTED_PLATFORMS.keys()),
        'formats': ['mp3', 'wav', 'm4a', 'flac', 'opus', 'vorbis'],
        'qualities': ['128', '192', '256', '320']
    })

@app.route('/status/<download_id>', methods=['GET'])
def status(download_id):
    """Récupère l'état d'un téléchargement"""
    if download_id not in downloads_status:
        return jsonify({'error': 'Téléchargement non trouvé'}), 404
    
    return jsonify(downloads_status[download_id])

@app.route('/file/<filename>', methods=['GET'])
def download_file(filename):
    """Télécharge le fichier MP3"""
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)