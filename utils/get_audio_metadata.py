import os
import time

from .cache_utils import (
    load_json_cache,
    save_json_cache,
    file_fingerprint,
    find_cache_entry_by_fingerprint,
)

CACHE_FILE = 'audio_metadata_cache.json'

try:
    from mutagen import File
except ModuleNotFoundError:
    File = None


def load_metadata_cache():
    return load_json_cache(CACHE_FILE)


def save_metadata_cache(cache):
    save_json_cache(CACHE_FILE, cache)


def _get_cached_metadata(file_path, fingerprint, cache):
    if not fingerprint:
        return None, cache

    path_key = os.path.abspath(file_path)
    entry = cache.get(path_key)
    if entry and entry.get('fingerprint') == fingerprint:
        return entry.get('metadata'), cache

    _, other_entry = find_cache_entry_by_fingerprint(cache, fingerprint)
    if other_entry and other_entry.get('metadata'):
        cache[path_key] = {
            'metadata': other_entry['metadata'],
            'fingerprint': fingerprint,
            'updated': time.time(),
        }
        return other_entry['metadata'], cache

    return None, cache


def get_audio_metadata(file_path):
    metadata = {
        "title": os.path.basename(file_path),
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "genre": "Unknown Genre",
        "duration": 0,
    }

    fingerprint = file_fingerprint(file_path)
    cache = load_metadata_cache()
    cached_metadata, cache = _get_cached_metadata(file_path, fingerprint, cache)
    if cached_metadata:
        return cached_metadata

    try:
        if File is None:
            raise RuntimeError('mutagen package is not installed')

        audio = File(file_path)

        if audio is not None:
            if getattr(audio, 'info', None):
                metadata["duration"] = audio.info.length

            if getattr(audio, 'tags', None):
                tags = audio.tags
                if 'TIT2' in tags:
                    metadata["title"] = str(tags.get('TIT2', [metadata["title"]])[0])
                elif 'title' in tags:
                    metadata["title"] = str(tags.get('title', [metadata["title"]])[0])

                artist = tags.get('TPE1') or tags.get('artist')
                if artist:
                    metadata["artist"] = str(artist[0])

                album = tags.get('TALB') or tags.get('album')
                if album:
                    metadata["album"] = str(album[0])

                genre = tags.get('TCON') or tags.get('genre')
                if genre:
                    metadata["genre"] = str(genre[0])
    except Exception as e:
        print(f"Metadata error for {file_path}: {e}")

    if fingerprint:
        cache[os.path.abspath(file_path)] = {
            'metadata': metadata,
            'fingerprint': fingerprint,
            'updated': time.time(),
        }
        save_metadata_cache(cache)

    return metadata
