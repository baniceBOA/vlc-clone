import os
from mutagen import File

def get_audio_metadata(file_path):
    metadata = {
        "title": os.path.basename(file_path),
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "genre": "Unknown Genre",
        "duration": 0
    }
    
    try:
        audio = File(file_path)
        
        if audio is not None:
            # 1. Get Duration (available on almost all formats)
            if audio.info:
                metadata["duration"] = audio.info.length
            
            # 2. Extract Tags (keys vary by format)
            # We use .get() because these fields might not exist in the file
            if audio.tags:
                # MP3/ID3 style
                if 'TIT2' in audio.tags:
                    metadata["title"] = str(audio.tags.get('TIT2', [metadata["title"]])[0])
                # OGG/FLAC/Vorbis style
                elif 'title' in audio.tags:
                    metadata["title"] = str(audio.tags.get('title', [metadata["title"]])[0])
                
                # Artist extraction
                artist = audio.tags.get('TPE1') or audio.tags.get('artist')
                if artist:
                    metadata["artist"] = str(artist[0])

                # Album extraction
                album = audio.tags.get('TALB') or audio.tags.get('album')
                if album:
                    metadata["album"] = str(album[0])
                genre = audio.tags.get('TCON') or audio.tags.get('genre')
                if genre:
                    metadata["genre"] = str(genre[0])
                    
    except Exception as e:
        print(f"Metadata error for {file_path}: {e}")
        
    return metadata