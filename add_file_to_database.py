import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

from get_settings import get_settings
from assistant import hash_file, MOVIE_EXTENSIONS, file_is_picture
from walk_pictures_and_build_database import File

user_settings = get_settings()
base = declarative_base()
engine = create_engine(get_settings().get('database'), echo=False)


class File(base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    uploaded = Column(Boolean, default=False)
    md5hash = Column(String)
    datetime = Column(String)
    is_movie = Column(Boolean, default=False)
    is_picture = Column(Boolean, default=False)


def main(args):
    base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for file_ in args:
        file_dict = {}

        if os.path.exists(file_):

            # md5hash
            file_dict['md5hash'] = hash_file(file_)

            # is_something
            _, extension = os.path.splitext(file_)
            if extension.lower() in MOVIE_EXTENSIONS:
                file_dict['is_movie'] = True
            elif file_is_picture(file_):
                file_dict['is_picture'] = True

            # filename
            file_dict['name'] = os.path.basename(file_)

            # filepath
            use_path = raw_input('Do you want to use this path as the DB entry? [Y/n]')
            if not use_path:
                use_path = 'y'

            assert use_path.lower().startswith('y') or use_path.lower().startswith('n')
            if use_path.lower().startswith('n'):
                file_dict['path'] = raw_input('Gimme the new path: ')
            else:
                file_dict['path'] = file_

            new_entry = File(**file_dict)
            session.add(new_entry)
            session.commit()


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
