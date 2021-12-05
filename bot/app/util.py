import requests
import binascii
import config
import time


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


class WatchTimer:
    def __init__(self):
        self.time = time.time()

    def update(self):
        self.time = time.time()

    def poll(self):
        return (abs(self.time - time.time())) > config.watch_check_timer


def is_valid_url(url):
    try:
        data = requests.get(url)
        return True
    except Exception:
        return False


def is_static_url(url):
    try:
        sum1 = crc32(get_data(url))
        sum2 = crc32(get_data(url))
        if sum1 != sum2:
            return False
        return True
    except Exception:
        return False


def page_size(url):
    try:
        headers = requests.head(url).headers
        return int(headers["Content-Length"])
    except Exception:
        return 0


def get_data(url):
    data = requests.get(url)
    data.encoding = "utf-8"
    data = data.text.strip()
    return data


def get_url(url):
    while url[-2] == "/" and url[-1] == "/":
        url = url[:-1]
    return url


def crc32(data):
    return int(binascii.crc32(data.encode("utf8")))
