from __future__ import print_function

from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

import os
import re
import shutil
import argparse

from get_settings import get_settings
from DBFileRecord import DBFileRecord, TimeStamp
from assistant import get_exif_data, MOVIE_EXTENSIONS, EXCLUDED_EXTENSIONS, file_is_picture, hash_file, mkdir_p

user_settings = get_settings()
base = declarative_base()
engine = create_engine(get_settings().get('database_url'), echo=False)


class File(base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    uploaded = Column(Boolean, default=False)
    md5hash = Column(String, unique=True)
    is_movie = Column(Boolean, default=False)
    is_picture = Column(Boolean, default=False)


def walk_picture_directory(directory):
    startswith_iso_fmt = re.compile(".*(?P<iso>20\d{6})[-_].*.jpg", re.IGNORECASE)

    base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for root, dirs, files in os.walk(directory):

        # uncomment this to exclude processed and notprocessed directories
        #dirs[:] = [d for d in dirs if d not in [user_settings.get('processed_directory'), user_settings.get('notprocessed_directory')]]

        for file_ in files:
            _, extension = os.path.splitext(file_)
            db_record = DBFileRecord(file_, os.path.join(root, file_))

            if extension.lower() in EXCLUDED_EXTENSIONS:
                continue

            db_record.md5hash = hash_file(db_record.path)

            if extension.lower() in MOVIE_EXTENSIONS:
                db_record.is_movie = True

                # uncomment to reintroduce file moving

                new_dir = os.path.join(user_settings.get('processed_directory'), 'movies')
                new_path = os.path.join(new_dir, db_record.name)

                if not os.path.exists(new_path):

                    shutil.move(db_record.path, new_path)
                    db_record.path = new_path
                else:
                    print("Did not move {}".format(db_record.path))


                file = File(name=db_record.name,
                            path=db_record.path,
                            md5hash=db_record.md5hash,
                            is_movie=db_record.is_movie)
                session.add(file)
                try:
                    session.commit()
                except sqlalchemy.exc.IntegrityError as e:
                    print(file_, e.args)
                    session.rollback()
                continue
            elif file_is_picture(db_record.path):
                db_record.is_picture = True

                if get_exif_data(db_record.path).get('DateTimeOriginal', None) is not None:
                    # have exif data
                    dto = get_exif_data(db_record.path).get('DateTimeOriginal')
                    timestamp = TimeStamp(dto)
                elif startswith_iso_fmt.search(db_record.name):
                    # have iso format
                    match_obj = startswith_iso_fmt.search(db_record.name)
                    iso = match_obj.group('iso')
                    time_string = ':'.join([iso[0:4], iso[4:6], iso[6:]]) + " 00:00:00"
                    timestamp = TimeStamp(time_string)
                else:
                    if not os.path.exists(db_record.path):
                        shutil.move(db_record.path, user_settings.get('notprocessed_directory'))
                    else:
                        print("Did not move {}".format(db_record.path))
                    continue
                # uncomment to restore file moving
                new_dir = os.path.join(user_settings.get('processed_directory'), timestamp.year, timestamp.month, timestamp.day)
                mkdir_p(new_dir)
                new_path = os.path.join(new_dir, db_record.name)
                if not os.path.exists(new_path):
                    shutil.move(db_record.path, new_path)
                    db_record.path = new_path
                else:
                    print("Did not move {}".format(db_record.path))

                file = File(name=db_record.name,
                            path=db_record.path,
                            md5hash=db_record.md5hash,
                            is_picture=db_record.is_picture)
                session.add(file)
                try:
                    session.commit()
                except sqlalchemy.exc.IntegrityError as e:
                    print(file_, e.args)
                    session.rollback()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='dir')

    namespace = parser.parse_args()
    print('if you think this will move files, think again, and check the comment sections to see if you commented that functionality out or not.')
    walk_picture_directory(namespace.dir)
