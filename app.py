from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import uuid
import threading

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """Get video information and available formats"""
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({'error': 'Could not fetch video information'}), 404
            
            # Extract video details
            video_data = {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'formats': []
            }
            
            # Process formats - filter for video+audio or video only
            seen_formats = set()
            for fmt in info.get('formats', []):
                # Skip formats without proper info
                if not fmt.get('format_id'):
                    continue
                
                # Get format description
                format_note = fmt.get('format_note', '')
                ext = fmt.get('ext', 'unknown')
                quality = fmt.get('quality', 0)
                resolution = fmt.get('resolution', 'N/A')
                filesize = fmt.get('filesize') or fmt.get('filesize_approx')
                vcodec = fmt.get('vcodec', 'none')
                acodec = fmt.get('acodec', 'none')
                
                # Create unique identifier for this format
                format_key = f"{resolution}_{ext}_{vcodec}_{acodec}"
                if format_key in seen_formats:
                    continue
                seen_formats.add(format_key)
                
                # Only include formats that have video
                if vcodec == 'none':
                    continue
                
                # Determine format type
                if acodec != 'none' and vcodec != 'none':
                    format_type = 'video+audio'
                elif vcodec != 'none':
                    format_type = 'video only'
                else:
                    continue
                
                format_info = {
                    'format_id': fmt.get('format_id'),
                    'format': fmt.get('format', ''),
                    'ext': ext,
                    'resolution': resolution,
                    'quality': quality,
                    'filesize': filesize,
                    'filesize_human': format_size(filesize),
                    'vcodec': vcodec,
                    'acodec': acodec,
                    'format_type': format_type,
                    'url': fmt.get('url', '')
                }
                
                video_data['formats'].append(format_info)
            
            # Sort formats by quality (higher first)
            video_data['formats'].sort(key=lambda x: x.get('quality', 0), reverse=True)
            
            return jsonify(video_data)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video with selected format"""
    data = request.json
    url = data.get('url', '')
    format_id = data.get('format_id', 'best')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/{unique_id}_%(title)s.%(ext)s',
            'format': format_id,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        downloaded_path = None
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the actual downloaded file path
            if info:
                downloaded_path = ydl.prepare_filename(info)
                # Handle cases where format changes extension
                if not os.path.exists(downloaded_path):
                    base_name = os.path.splitext(downloaded_path)[0]
                    for ext in ['mp4', 'webm', 'mkv', 'flv']:
                        test_path = f"{base_name}.{ext}"
                        if os.path.exists(test_path):
                            downloaded_path = test_path
                            break
        
        if downloaded_path and os.path.exists(downloaded_path):
            return jsonify({
                'success': True,
                'filename': os.path.basename(downloaded_path),
                'path': downloaded_path
            })
        else:
            return jsonify({'error': 'Download failed - file not found'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-file/<filename>')
def serve_file(filename):
    """Serve the downloaded file"""
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/formats', methods=['GET'])
def list_downloads():
    """List all downloaded files"""
    files = []
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            files.append({
                'filename': filename,
                'size': format_size(size),
                'download_url': f'/api/download-file/{filename}'
            })
    return jsonify(files)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting YouTube Video Downloader Server...")
    print("Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
