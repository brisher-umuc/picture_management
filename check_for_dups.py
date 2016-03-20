"""
Updated:  29 Nov 2015
python check_for_dups.py <PATH_TO_DIRECTORY>

if you still trust yourself... run the command below to clean up the pictures folder.
python check_for_dups.py /mnt/nfs/storage/pictures/

works on one pass of the directory, is recursive, beware
"""
#TODO:  not optimized, super slow on large directories, check for filesize, etc...

import argparse
import os
import collections
import hashlib
import sqlite3

from assistant import file_is_picture
from get_settings import get_settings

user_settings = get_settings()

def connect_to_database(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    return cursor

# connect to db specified in settings.config
database = user_settings.get('database')
curs = connect_to_database(database)

def check_for_duplicates(directory):
    picture_dict = collections.defaultdict(list)

    for root, subdirs, files in os.walk(directory):
        for file_ in files:
            file_ = os.path.join(root, file_)
            try:
                if not os.path.isfile(file_) or not file_is_picture(file_):  # is not a picture or not a file
                    continue
            except IOError:
                print('skipping:', file_)
                continue
            with open(file_, 'rb') as f:
                md5 = hashlib.md5()
                md5.update(f.read())
                digest = md5.hexdigest()
            
            #file has already been processed into the db, don't care about it
            if hash_is_in_database(digest):
                os.remove(file_)
            else:
                picture_dict[digest].append(file_)  # md5 is the key, all files that match that md5 are in the list

    for md5hash, pic_list in picture_dict.items():
        if len(pic_list) > 1:
            print(md5hash, pic_list)
            for i, pic in enumerate(pic_list):
                if i == 0:
                    continue
                print('removing:', pic)
                os.remove(os.path.join(directory, pic))



def hash_is_in_database(md5):
    return curs.execute('select count(*) from files where md5hash=?', (md5,)).fetchone()[0] > 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='dir', default='.')

    namespace = parser.parse_args()
    check_for_duplicates(namespace.dir)

