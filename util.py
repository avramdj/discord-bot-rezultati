import requests
import datetime
import binascii

class DbEntry:
    def __init__(self, ctx, url, data):
        self.ctx = [CtxEntry(ctx).__dict__]
        self.url = url
        self.checksum = crc32(data)
    def dict(self):
        return self.__dict__

class CtxEntry:
    def __init__(self, ctx):
        self.author = str(ctx.author)
        self.mention = str(ctx.author.mention)
        self.channel = str(ctx.channel.id)
    def dict(self):
        return self.__dict__

def is_valid_url(url):
    try:
        data = requests.get(url)
        return True
    except Exception:
        return False

def get_data(url):
    data = requests.get(url).text.strip()
    return data

def crc32(data):
    return int(binascii.crc32(data.encode('utf8')))