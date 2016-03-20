#!/usr/bin/python2
from __future__ import print_function

from sqlalchemy import create_engine
from sqlalchemy.sql import select

import flickrapi
import webbrowser
import sqlite3

from get_settings import get_settings

user_settings = get_settings()
FALSE = ID = 0
TRUE = 1
PATH = 2

def main():
    print('Step 1: authenticate')
    flickr = flickrapi.FlickrAPI(user_settings.get('api_key'), user_settings.get('api_secret'))

    # Only do this if we don't have a valid token already
    if not flickr.token_valid(perms=u'write'):

        # Get a request token
        flickr.get_request_token(oauth_callback='oob')

        # Open a browser at the authentication URL. Do this however
        # you want, as long as the user visits that URL.
        authorize_url = flickr.auth_url(perms=u'write')
        webbrowser.open_new_tab(authorize_url)

        # Get the verifier code from the user. Do this however you
        # want, as long as the user gives the application the code.
        verifier = unicode(raw_input('Verifier code: '))

        # Trade the request token for an access token
        flickr.get_access_token(verifier)
    print('Step 2: get pictures in database that arent uploaded yet')
    conn = sqlite3.connect(user_settings.get('database'))
    curs = conn.cursor()
    data = curs.execute("SELECT * FROM files WHERE uploaded = ?", (FALSE,)).fetchall()
    #import pdb;pdb.set_trace()

    log = open('flickrupload.log', 'a')
    print('Step 3: begin uploading')

    for i, row in enumerate(data):
        print(row)
        log.write(str(row) + '\n')
        try:
            flickr.upload(filename=row[PATH], is_public=0)
        except Exception as e:
            print('Exception during upload of', row)
            log.write('Exception during upload of ' + str(row) + '\n')
            log.write('Exception: ' + str(e))
            flickr = flickrapi.FlickrAPI(user_settings.get('api_key'), user_settings.get('api_secret'))
            continue
        try:
            curs.execute('update files set uploaded = ? where id = ?', (TRUE, row[ID]))
        except Exception as e:
            print('Exception during upload of', row)
            log.write('Exception during upload of ' + str(row) + '\n')
            log.write('Exception: ' + str(e))
            continue

        log.flush()
        conn.commit()

    conn.close()
    log.close()


if __name__ == '__main__':
    main()
