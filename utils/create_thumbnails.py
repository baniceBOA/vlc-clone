import cv2
import os


def create_thumbnail(filename, output_dir=None):
    ''' filename the file of the video to create thumbnail
        output_dir=None the output directory to store the thumbnail

    '''
    thumbname = f'{os.path.splitext(filename.split(os.sep)[-1])[0]}.png'
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