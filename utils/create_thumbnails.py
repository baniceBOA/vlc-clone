
import os
import hashlib
import time
from kivy.app import App
from kivy.utils import platform
from kivy.resources import resource_find

from .cache_utils import (
    load_json_cache,
    save_json_cache,
    file_fingerprint,
    find_cache_entry_by_fingerprint,
    make_content_hash,
)

CACHE_FILE = 'thumbnail_cache.json'


def get_thumbnail_dir():
    app = App.get_running_app()
    if app and platform == 'android':
        return os.path.join(app.user_data_dir, 'assests', 'thumbs')
    return os.path.join('assests', 'thumbs')


def load_thumbnail_cache():
    return load_json_cache(CACHE_FILE)


def save_thumbnail_cache(cache):
    save_json_cache(CACHE_FILE, cache)


def _find_existing_thumbnail(filename, output_dir, cache, fingerprint):
    if not fingerprint:
        return None, cache

    path_key = os.path.abspath(filename)
    existing = cache.get(path_key)
    if existing and existing.get('fingerprint') == fingerprint:
        thumb = existing.get('thumb')
        if thumb and os.path.exists(thumb):
            return thumb, cache

    old_path, old_entry = find_cache_entry_by_fingerprint(cache, fingerprint)
    if old_entry:
        thumb = old_entry.get('thumb')
        if thumb and os.path.exists(thumb):
            cache[path_key] = {
                'thumb': thumb,
                'fingerprint': fingerprint,
                'updated': time.time(),
            }
            return thumb, cache

    basename = os.path.splitext(os.path.basename(filename))[0]
    if output_dir and os.path.isdir(output_dir):
        for candidate in os.listdir(output_dir):
            if candidate.startswith(basename) and candidate.lower().endswith('.png'):
                candidate_path = os.path.join(output_dir, candidate)
                if os.path.exists(candidate_path):
                    cache[path_key] = {
                        'thumb': candidate_path,
                        'fingerprint': fingerprint,
                        'updated': time.time(),
                    }
                    return candidate_path, cache

    return None, cache


def create_thumbnail(filename, output_dir=None):
    ''' filename the file of the video to create thumbnail
        output_dir=None the output directory to store the thumbnail
    '''
    if not output_dir:
        output_dir = get_thumbnail_dir()
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fingerprint = file_fingerprint(filename)
    if not fingerprint:
        return None

    cache = load_thumbnail_cache()
    cached_thumb, cache = _find_existing_thumbnail(filename, output_dir, cache, fingerprint)
    if cached_thumb:
        save_thumbnail_cache(cache)
        return cached_thumb

    thumbname = f"{os.path.splitext(os.path.basename(filename))[0]}_{make_content_hash(os.path.abspath(filename))}.png"
    thumb_path = os.path.join(output_dir, thumbname)

    try:
        import cv2

        vcap = cv2.VideoCapture(filename)
        res, im_ar = vcap.read()

        if res:
            while im_ar.mean() < 10 and res:
                res, im_ar = vcap.read()
            im_ar = cv2.resize(im_ar, (400, 400), 0, 0, cv2.INTER_LINEAR)
            cv2.imwrite(thumb_path, im_ar)

            cache[os.path.abspath(filename)] = {
                'thumb': thumb_path,
                'fingerprint': fingerprint,
                'updated': time.time(),
            }
            save_thumbnail_cache(cache)
            return thumb_path
        return None
    except Exception as e:
        print(f'Failed with error:{e}')
        try:
            from moviepy.editor import VideoFileClip
            from PIL import Image

            clips = VideoFileClip(filename)
            max_duration = int(clips.duration) + 1
            mid = max_duration // 2
            frame = clips.get_frame(mid)
            thumbnail = Image.fromarray(frame)
            thumbnail.save(thumb_path)

            cache[os.path.abspath(filename)] = {
                'thumb': thumb_path,
                'fingerprint': fingerprint,
                'updated': time.time(),
            }
            save_thumbnail_cache(cache)
            return thumb_path
        except Exception:
            print('Failed to create a thumbname using default')
            from PIL import Image
            default_path = resource_find(os.path.join('assests', 'thumbs', 'videothumb.png'))
            if not default_path:
                default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assests', 'thumbs', 'videothumb.png')
            defaultimage = Image.open(default_path)
            defaultimage.save(thumb_path)

            cache[os.path.abspath(filename)] = {
                'thumb': thumb_path,
                'fingerprint': fingerprint,
                'updated': time.time(),
            }
            save_thumbnail_cache(cache)
            return thumb_path




