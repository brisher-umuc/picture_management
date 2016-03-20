from __future__ import print_function
from PIL import Image
from PIL.ExifTags import TAGS
import imghdr
import hashlib
import os
import errno
import shutil


POSSIBLE_PIC_FMTS = ['rbg', 'gif', 'pbm', 'pgm', 'ppm', 'tiff', 'rast', 'xbm', 'jpeg', 'bmp', 'png']
MOVIE_EXTENSIONS = ['.mp4', '.avi', '.mov']
EXCLUDED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.pdi', '.cpi', '.3gp', '.bdm', '.mpl',
                       '.tid', '.nomedia', '.thumb']


def file_is_picture(path_to_file):
    return imghdr.what(path_to_file) in POSSIBLE_PIC_FMTS


def get_exif_data(file_name):
    """ Get embedded EXIF data from image file.

    :return: dictionary of exif data
    """
    ret = {}
    try:
        img = Image.open(file_name)
        if hasattr(img, '_getexif'):
            exif_info = img._getexif()
            if exif_info is not None:
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError as e:
        print('IO ERROR:', file_name)
        print(e)
    return ret


def hash_file(path_to_file):
    with open(path_to_file, 'rb') as f:
        md5 = hashlib.md5()
        md5.update(f.read())
        return md5.hexdigest()


def mkdir_p(path):
    """ mkdir -p functionality """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def move_file(source, destination, increment=0):
    if os.path.exists(destination):
        move_file(source, "{}-{}".format(destination, increment), increment + 1)
    else:
        shutil.move(source, destination)
