
import os


def create_thumbnail(filename, output_dir=None):
    ''' filename the file of the video to create thumbnail
        output_dir=None the output directory to store the thumbnail

    '''
    thumbname = f'{os.path.splitext(filename.split(os.sep)[-1])[0]}.png'
    try:
        import  cv2
        vcap = cv2.VideoCapture(filename)
        res, im_ar = vcap.read()
        
        if res:
            while im_ar.mean() < 10 and res:
                res, im_ar = vcap.read()
            im_ar = cv2.resize(im_ar, (400, 400), 0, 0, cv2.INTER_LINEAR)
            #to save we have two options
            #1) save on a file
            if output_dir:
                cv2.imwrite(os.path.join(output_dir, thumbname), im_ar)
                return os.path.join(output_dir, thumbname)
            else:
                cv2.imwrite(thumbname, im_ar)
                return thumbname
        else:
            return None
    except Exception as e:
        print(f'Failed with error:{e}')
        try:
            from moviepy.editor import VideoFileClip
            from PIL import Image
            clips = VideoFileClip(filename)
            frames = clips.reader.fps
            max_duration = int(clips.duration)+1
            mid = max_duration//2

            frame = clips.get_frame(mid)
            thumbnail = Image.fromarray(frame)
            if output_dir:
                thumbnail.save(os.path.join(output_dir, thumbname))
                return os.path.join(output_dir, thumbname)
            else:
                thumbnail.save(thumbname)
                return thumbname
        except Exception as e:
            print('Failed to create a thumbname using default')
            from PIL import Image
            defaultimage = Image.open('/assests/thumbs/videothumb.png')
            if output_dir:
                defaultimage.save(os.path.join(output_dir, thumbname))
                return os.path.join(output_dir, thumbname)
            else:
                defaultimage.save(thumbname)
                return thumbname




