import flickrapi
import sqlite3

from get_settings import get_settings

user_settings = get_settings()

FALSE = 0
TRUE = 1
PATH = 2

class FlickrSession():
    def __init__(self):
        self.flickr = flickrapi.FlickrAPI(user_settings.get('api_key'), user_settings.get('api_secret'))

    def get_picture_list(self, page='1'):
        return self.flickr.people.getPhotos(api_key=user_settings.get('api_key'), user_id=user_settings.get('user_id'), page=str(page))

    def get_number_of_pages(self, response):
        return int(response.find('photos').get('pages'))

    def main(self):
        from collections import defaultdict
        flickr_list = defaultdict(list)
        #conn = sqlite3.connect('/home/ben/MyScripts/picture_management/picture_database.db')
        #curs = conn.cursor()

        for page in xrange(1, int(self.get_number_of_pages(self.get_picture_list()))):
            response = self.get_picture_list(page)
            photos = response.find('photos').findall('photo')
            for photo in photos:
                #curs.execute('update files set uploaded = ? where name = ?', (TRUE, photo.get('title')))
                flickr_list[photo.get('title')].append(photo.get('id'))
                #import pdb; pdb.set_trace()
                #conn.commit()

        
        import collections
        #duplicates = [x for x, count in dict(collections.Counter(flickr_list)).items() if count > 1]
        duplicates = [x[1] for k, x in flickr_list.items() if len(x) > 1]
        for photo_id in duplicates:
            #import pdb; pdb.set_trace()
            self.flickr.photos.delete(api_key=user_settings.get('api_key'), photo_id=photo_id)
        #print('Duplicates incoming')
        #for d in duplicates:
            #print(d)
        #conn.close()
        #data = curs.execute("SELECT * FROM files WHERE uploaded = ?", (TRUE,)).fetchall()

        #curs.execute('update files set uploaded = ? where id = ?', (TRUE, row[ID]))
    
if __name__ == '__main__':
    flickr_session = FlickrSession()
    flickr_session.main()
