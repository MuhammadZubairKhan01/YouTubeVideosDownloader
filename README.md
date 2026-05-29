# YouTube Video Downloader

A real-time working YouTube video downloader web application that allows users to paste any YouTube video link, view available download formats with sizes, and download videos directly to local storage.

## Features

- ✅ Real-time video information fetching
- ✅ Display video thumbnail, title, duration, uploader, and view count
- ✅ Show all available download formats with resolution, file size, and codec info
- ✅ Choose quality from 144p to 4K (2160p)
- ✅ Download videos directly to local storage
- ✅ View history of downloaded files
- ✅ Clean, modern UI with responsive design
- ✅ Progress indicator during downloads

## Running the Application

The server is already running on `http://localhost:5000`

To restart:
```bash
cd /workspace
python3 app.py
```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Paste any YouTube video URL into the input field
3. Click "Fetch Video" button
4. Review the video information and available formats
5. Click "Download" on your preferred format
6. The video will be downloaded to your local storage

## API Endpoints

### GET `/`
Serves the main HTML page

### POST `/api/info`
Fetches video information and available formats

### POST `/api/download`
Downloads a video in the specified format

### GET `/api/download-file/<filename>`
Serves the downloaded file for browser download

### GET `/api/formats`
Lists all downloaded files

## File Structure

```
/workspace/
├── app.py              # Flask backend server
├── templates/
│   └── index.html      # Frontend HTML/CSS/JS
├── downloads/          # Downloaded videos storage
└── README.md           # This file
```

## Technical Details

- **Backend**: Flask (Python web framework)
- **Video Processing**: yt-dlp (YouTube download library)
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **CORS**: Enabled for cross-origin requests

## Notes

- Videos are stored in the `downloads/` folder
- Each download gets a unique ID prefix to avoid filename conflicts
- The application supports various YouTube video qualities and formats

## License

This project is for educational purposes only. Please respect YouTube's Terms of Service and copyright laws when downloading videos.
