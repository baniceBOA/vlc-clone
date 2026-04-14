import json
import os
import hashlib
import time
from kivy.app import App

CACHE_FILENAME = 'vlcclone_cache.json'


def get_cache_dir():
    app = App.get_running_app()
    if app and hasattr(app, 'user_data_dir'):
        cache_dir = app.user_data_dir
    else:
        cache_dir = os.path.join(os.path.expanduser('~'), '.vlcclone')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_cache_path(filename):
    return os.path.join(get_cache_dir(), filename)


def load_json_cache(filename):
    path = get_cache_path(filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def save_json_cache(filename, data):
    try:
        path = get_cache_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def file_fingerprint(path):
    try:
        stat = os.stat(path)
        return {
            'size': stat.st_size,
            'mtime': stat.st_mtime,
        }
    except Exception:
        return None


def fingerprint_key(fingerprint):
    if not fingerprint:
        return None
    return f"{fingerprint['size']}:{fingerprint['mtime']}"


def find_cache_entry_by_fingerprint(cache, fingerprint):
    if not fingerprint:
        return None, None
    for cached_path, entry in cache.items():
        if entry.get('fingerprint') == fingerprint:
            return cached_path, entry
    return None, None


def make_content_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]
