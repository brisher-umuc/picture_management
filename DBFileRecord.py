class DBFileRecord:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.uploaded = False
        self.md5hash = None
        self.datetime = None
        self.is_movie = False
        self.is_picture = False


class TimeStamp:
    def __init__(self, time_string):
        date, time = time_string.split()
        self.year, self.month, self.day = date.split(':')
        self.hour, self.minute, self.second = time.split(':')
        self.time_string = time_string

    def __str__(self):
        return self.time_string