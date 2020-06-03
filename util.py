import requests
import datetime
import binascii

class DbEntry_URL:
    def __init__(self, ctx, url, data):
        self.ctx = [CtxEntry(ctx).__dict__]
        self.url = url
        self.checksum = crc32(data)
    def dict(self):
        return self.__dict__


class DbEntry_USER:
    def __init__(self, ctx, url):
        self.user = str(ctx.author)
        self.id = ctx.author.id
        self.mention = str(ctx.author.mention)
        self.urls = [url]
    def dict(self):
        return self.__dict__


class CtxEntry:
    def __init__(self, ctx):
        self.author = str(ctx.author)
        self.id = str(ctx.author.id)
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

def is_static_url(url):
    sum1 = crc32(get_data(url))
    sum2 = crc32(get_data(url))
    if sum1 != sum2:
        return False
    return True

def get_data(url):
    data = requests.get(url).text.strip()
    return data

def crc32(data):
    return int(binascii.crc32(data.encode('utf8')))