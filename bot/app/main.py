import discord
import pymongo
import config
from util import *
from discord.ext import commands
from asyncio import sleep
import time
import messages
import sys
import os

intents = discord.Intents.default()
client = commands.Bot(command_prefix=("sudo ", "Sudo "), intents=intents)
mongo_client = pymongo.MongoClient(config.db_uri)
db = mongo_client[config.db_name]
db_urls = db["urls"]
db_users = db["users"]
db_store = db["store"]
channels = []
client.remove_command("help")
watch_timer = WatchTimer()
secret_channel = os.environ["SECRET_SERVER"]


@client.event
async def on_ready():
    await log("Inicijalizacija gotova!")
    activity = discord.Activity(name="MATF", type=discord.ActivityType.watching)
    await client.change_presence(activity=activity, status=discord.Status.idle)


@client.command(name="prati", pass_context=True, aliases=["zaprati", "+"])
async def prati(ctx, *args):
    begin_t = time.time()
    if len(args) == 0:
        await ctx.send(messages.need_url)
        return

    url = get_url(args[-1])
    query = db_urls.find_one({"url": url})

    if query is not None:
        for ctxx in query["ctx"]:
            if ctxx["id"] == str(ctx.author.id):
                await ctx.send(f"{ctx.author.mention} {messages.already_following}")
                return

    if not is_valid_url(url):
        await ctx.send(messages.invalid_url)
        return

    if page_size(url) >= config.page_size_max:
        await ctx.send(messages.page_too_big)
        return

    if not is_static_url(url):
        await ctx.send(messages.not_static)
        return

    try:
        data = get_data(url)
    except Exception as e:
        await ctx.send(f"{messages.request_error}" + "\n" + str(e))
        return False

    try:
        if query is not None:
            db_urls.update_one({"url": url}, {"$push": {"ctx": CtxEntry(ctx).__dict__}})
        else:
            db_urls.insert_one(DbEntry_URL(ctx, url, data).__dict__)
        query = db_users.find_one({"id": ctx.author.id})
        if query is not None:
            db_users.update_one({"id": ctx.author.id}, {"$push": {"urls": url}})
        else:
            db_users.insert_one(DbEntry_USER(ctx, url).__dict__)
    except Exception as e:
        await ctx.send(f"{messages.db_error}" + "\n" + str(e))
        return

    await ctx.send(f"{ctx.author.mention} {messages.success_follow}")
    await log(
        str(ctx.author)
        + " je zapratio "
        + get_url(args[-1])
        + " "
        + "{:.2f}s".format(time.time() - begin_t)
    )


@client.command(name="otprati", aliases=["-"])
async def otprati(ctx, *args):
    if len(args) == 0:
        await ctx.send(messages.need_url)
        return

    if args[-1].strip() == "sve":
        db_urls.update_many({}, {"$pull": {"ctx": {"id": str(ctx.author.id)}}})
        try:
            db_users.update_one({"id": ctx.author.id}, {"$set": {"urls": []}})
        except:
            await ctx.send(f"{messages.db_error}")
            return
        await ctx.send(f"{ctx.author.mention} {messages.success_unfollow}")
        return
    else:
        url = get_url(args[-1])
        db_urls.update_one({"url": url}, {"$pull": {"ctx": {"id": str(ctx.author.id)}}})
        try:
            db_urls.update_one(
                {"url": url}, {"$pull": {"ctx": {"id": str(ctx.author.id)}}}
            )
            db_users.update_one({"id": ctx.author.id}, {"$pull": {"urls": url}})
        except:
            await ctx.send(f"{messages.db_error}")

        await ctx.send(f"{ctx.author.mention} {messages.success_unfollow}")
    await log(str(ctx.author) + " je otpratio " + get_url(args[-1]))


@client.command(name="strane", aliases=["list"])
async def strane(ctx, *args):
    user_entry = db_users.find_one({"id": ctx.author.id})
    message = ""
    if user_entry is None or len(user_entry["urls"]) == 0:
        await ctx.send(f"{str(ctx.author.mention)} {messages.following_zero}")
        return
    for url in user_entry["urls"]:
        message += "<" + url + ">" + "\n"
    await bufsend(ctx, message, mention=True)


@client.command(name="users", aliases=["korisnici"])
async def users(ctx, *args):
    try:
        users = db_users.find({})
        message = "Svi korisnici u bazi:\n"
        exists = False
        usernames = []
        for user in users:
            username = user["user"].split("#")
            usernames.append(username[0] + "[" + str(len(user["urls"])) + "]")
            exists = True
        if not exists:
            await ctx.send(f"{messages.no_users}")
        else:
            message += ", ".join(usernames)
            await bufsend(ctx, message)
    except Exception as e:
        await log(messages.db_error + str(e))


@client.command(name="sve", aliases=["links"])
async def sve(ctx, *args):
    try:
        urls = db_urls.find({})
        header = "Sve strane u bazi:\n"
        message_arr = []
        exists = False
        for url in urls:
            message_arr.append(("<" + url["url"] + ">", len(url["ctx"])))
            exists = True
        if not exists:
            await ctx.send(f"{messages.no_pages}")
        else:
            message_arr.sort(key=lambda x: -x[1])
            message = header
            for (x, y) in message_arr:
                message += f"[{str(y)}] {x}\n"
            await bufsend(ctx, message)
    except Exception as e:
        await log(messages.db_error + str(e))


@client.command(name="help", aliases=["?"])
async def _help(ctx):
    await ctx.send(messages.command_list)


@client.command(name="aliases")
async def aliases(ctx):
    await ctx.send(messages.aliases)


@client.command(name="owner")
async def owner(ctx, *args):
    await ctx.send(messages.bot_owner)


@client.command(name="kraljevo")
async def kraljevo(ctx):
    await ctx.send("https://i.ibb.co/Y2kJ8bL/Screenshot-20200901-162933-1.jpg")


@client.command(name="pancevo")
async def kraljevo(ctx):
    await ctx.send(
        "https://media.discordapp.net/attachments/890367285171216384/895410398214377512/meme.png"
    )


@client.command(name="kompot")
async def kompot(ctx):
    await ctx.send("https://i.ibb.co/jM82dfw/IMG-20210106-212424-944.png")


@client.command(name="get", aliases=["g", "-g"])
async def get(ctx, *args):
    if ctx.guild.id != secret_channel:
        return
    if len(args) < 1:
        return await ctx.send("sudo get key")
    key = args[-1].strip()
    kv = db_store.find_one({"key": key})
    if kv is not None:
        await ctx.send(kv["value"])


@client.command(name="put", aliases=["p", "-p"])
async def put(ctx, *args):
    if ctx.guild.id != secret_channel:
        return
    await log(f"putting {args}")
    if len(args) < 2:
        return await ctx.send("sudo put key value")
    key = args[0].strip()
    val = " ".join(args[1:])
    kv = db_store.find_one({"key": key})
    if kv is None:
        try:
            db_store.insert_one({"key": key, "value": val, "owner": ctx.author.id})
            return await ctx.send("ok")
        except:
            return await ctx.send("Greska u bazi")
    else:
        return await ctx.send("Vec postoji")


@client.command(name="delete", aliases=["rm", "-rm"])
async def rm(ctx, *args):
    if ctx.guild.id != secret_channel:
        return
    await log(f"rm {args}")
    if len(args) < 1:
        return await ctx.send("sudo delete key")
    key = args[-1].strip()
    kv = db_store.find_one({"key": key})
    if kv is None:
        return await ctx.send("Kljuc ne postoji")
    elif kv["owner"] != ctx.author.id:
        return await ctx.send(
            f"Samo {client.get_user(int(kv['owner'])).name} ima dozvolu za to"
        )
    else:
        try:
            db_store.delete_one({"key": key})
            return await ctx.send("ok")
        except:
            return await ctx.send("Greska u bazi")


@client.command(name="keys", aliases=["k", "-k"])
async def keyss(ctx):
    if ctx.guild.id != secret_channel:
        return
    try:
        keys = db_store.find({})
        kk = ", ".join([x["key"] for x in keys])
        return await ctx.send(f"{kk}")
    except e:
        return await ctx.send(f"greska u bazi {e}")


async def watch():
    await client.wait_until_ready()
    while not client.is_closed():
        await sleep(config.sleep_duration)
        await log("Updatujem strane!")
        begin_t = time.time()
        urls = db_urls.find()
        for url in urls:
            try:
                new_checksum = crc32(get_data(url["url"]))
            except Exception as e:
                await log(
                    "Greska prilikom updatovanja strane " + url["url"] + "\n" + str(e)
                )
                continue
            if url["checksum"] != new_checksum:
                for ctx in url["ctx"]:
                    curr_user = client.get_user(int(ctx["id"]))
                    if curr_user:
                        await curr_user.send(messages.page_changed + "\n" + url["url"])
                        await log(
                            ctx["author"] + " je obavesten(a) o promeni " + url["url"]
                        )
                    else:
                        await log(
                            ctx["author"]
                            + f" {curr_user}::{ctx['id']}"
                            + " NIJE obavesten(a) o promeni "
                            + url["url"]
                        )
                db_urls.update_one(
                    {"url": url["url"]}, {"$set": {"checksum": new_checksum}}
                )
        await log("Strane updatovane za " + "{:.2f}s".format(time.time() - begin_t))
        watch_timer.update()


async def cleaner():
    await client.wait_until_ready()
    while not client.is_closed():
        await log("Cistim bazu...")
        try:
            begin_t = time.time()
            db_urls.delete_many({"ctx": {"$exists": "true", "$size": 0}})
            await log("Baza ociscena za " + "{:.2f}s".format(time.time() - begin_t))
        except Exception as e:
            await log(messages.db_error + "\n" + str(e))
        await sleep(config.prune_period)
        if watch_timer.poll():
            await log(messages.rebooting)
            sys.exit(1)


async def log(string):
    print(string)
    log_channel = client.get_channel(config.log_channel_id)
    print(log_channel)
    await log_channel.send(string)


async def bufsend(ctx, message, mention=False, dm=False):
    bufsiz = 2000
    mention_string = ""
    if mention:
        mention_string = ctx.author.mention + "\n"
        bufsiz -= len(mention_string)
    destination = ctx
    if dm:
        destination = client.get_user(ctx.author.id)
    chunks = []
    lines = message.split("\n")
    curlen = 0
    buf = ""
    for line in lines:
        line += "\n"
        curlen += len(line)
        if curlen > bufsiz:
            chunks.append(buf)
            buf = ""
            curlen = len(line)
        buf += line
    if buf != "":
        chunks.append(buf)
    for chunk in chunks:
        msgbuf = mention_string + chunk
        await destination.send(msgbuf)


client.loop.create_task(watch())
client.loop.create_task(cleaner())
client.run(config.token)
