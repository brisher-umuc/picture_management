#!/bin/bash

PICDIR=/mnt/storage/ftp/sarah/ftp_upload/inbox
LOCKDIR=/tmp/BXgqg0looey7p9L9NZjIuaqvu7ANILL4foeqzpJcTs3YkwtiJ0
DATABASE=/mnt/storage/pictures/picture_database.db

mkdir $LOCKDIR  || {
    exit 1
    }
trap "rmdir $LOCKDIR" EXIT INT KILL TERM

if [ "`ls -A $PICDIR`" ]; then
  cd /root/picture_management
  /usr/bin/python2.7 check_for_dups.py $PICDIR
  /usr/bin/python2.7 walk_pictures_and_build_database.py $PICDIR
  /usr/bin/python2.7 authenticate_flickr.py
elif [ `sqlite3 $DATABASE "select count(*) from files where uploaded=0;"` -gt 0 ]; then 
  cd /root/picture_management
  /usr/bin/python2.7 authenticate_flickr.py
fi
