import discord
import pymongo
import config
from util import *
from discord.ext import commands
from asyncio import sleep
import time
import messages
from datetime import date
import traceback

client = commands.Bot(command_prefix='sudo ', case_insensitive=True)
mongo_client = pymongo.MongoClient(config.dbURI)
db = mongo_client[config.dbNAME]
db_urls = db['urls']
db_users = db['users']
channels = []
client.remove_command('help')

@client.event
async def on_ready():
    await log("Inicijalizacija gotova!")
    activity = discord.Activity(name='MATF', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity, status=discord.Status.idle)

@client.command(name='prati', pass_context=True, aliases=['zaprati', '+'])
async def prati(ctx, *args):
    begin_t = time.time()
    if len(args) == 0:
        await ctx.send(messages.need_url)
        return

    url = get_url(args[-1])
    query = db_urls.find_one({'url' : url})

    if query is not None:
        for ctxx in query['ctx']:
            if ctxx['author'] == str(ctx.author):
                await ctx.send(f'{ctx.author.mention} {messages.already_following}')
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
        await ctx.send(f'{messages.request_error}' + '\n' + str(e))
        return False

    try:
        if query is not None:
            db_urls.update_one({'url' : url}, {'$push' : { 'ctx' : CtxEntry(ctx).__dict__}})
        else:
            db_urls.insert_one(DbEntry_URL(ctx, url, data).__dict__)
        query = db_users.find_one({'id' : ctx.author.id})
        if query is not None:
            db_users.update_one({'id' : ctx.author.id}, {'$push' : { 'urls' : url}})
        else:
            db_users.insert_one(DbEntry_USER(ctx, url).__dict__)
    except Exception as e:
        await ctx.send(f'{messages.db_error}' + '\n' + str(e))
        return

    await ctx.send(f'{ctx.author.mention} {messages.success_follow}')
    await log(str(ctx.author) + " je zapratio " + get_url(args[-1]) + " " + "{:.2f}s".format(time.time() - begin_t))

@client.command(name='otprati', aliases=['-'])
async def otprati(ctx, *args):
    if len(args) == 0:
        await ctx.send(messages.need_url)
        return

    if args[-1].strip() == 'sve':
        db_urls.update_many({}, {'$pull' : {'ctx' : {'author' : str(ctx.author)}}}) 
        try:
            db_users.update_one({'id' : ctx.author.id} , {'$set' : {'urls' : []}})
        except:
            await ctx.send(f'{messages.db_error}')
            return
        await ctx.send(f'{ctx.author.mention} {messages.success_unfollow}')
        return
    else:
        url = get_url(args[-1])
        db_urls.update_one({"url": url}, {'$pull' : {'ctx' : {'author' : str(ctx.author)}}})
        try:
            db_urls.update_one({"url": url}, {'$pull' : {'ctx' : {'author' : str(ctx.author)}}})
            db_users.update_one({'id' : ctx.author.id}, {'$pull' : { 'urls' : url }})
        except:
            await ctx.send(f'{messages.db_error}')

        await ctx.send(f'{ctx.author.mention} {messages.success_unfollow}')
    await log(str(ctx.author) + " je otpratio " + get_url(args[-1]))

@client.command(name='strane', aliases=['list'])
async def strane(ctx, *args):
    user_entry = db_users.find_one({'id' : ctx.author.id})
    message = str(ctx.author.mention) + " "
    if user_entry is None or len(user_entry['urls']) == 0:
        await ctx.send(f'{str(ctx.author.mention)} {messages.following_zero}')
        return
    for url in user_entry['urls']:
        message += "<" + url + ">" + "\n"
    await ctx.send(message)

@client.command(name='users', aliases=['korisnici'])
async def sve(ctx, *args):
    users = db_users.find({})
    message = "Svi korisnici u bazi:\n"
    exists = False
    for user in users:
        username = user['user'].split('#')
        message += username[0] + "[" + str(len(user['urls'])) + "]" + ", "
        exists = True
    if not exists:
        await ctx.send(f'{messages.no_users}')
    else:
        message = message.rstrip(', ')
        await ctx.send(message)

@client.command(name='sve', aliases=['links'])
async def sve(ctx, *args):
    urls = db_urls.find({})
    message = "Sve strane u bazi:\n"
    exists = False
    for url in urls:
        message += "<" + url['url'] + ">" + "\n"
        exists = True
    if not exists:
        await ctx.send(f'{messages.no_pages}')
    else:
        await ctx.send(message)

@client.command(name='help', aliases=['?'])
async def _help(ctx):
    await ctx.send(messages.command_list)

@client.command(name='aliases')
async def aliases(ctx):
    await ctx.send(messages.aliases)

@client.command(name='owner')
async def owner(ctx, *args):
    await ctx.send(messages.bot_owner)

async def watch():
    await client.wait_until_ready()
    while not client.is_closed():
        await sleep(config.sleep_duration)
        await log("Updatujem strane!")
        begin_t = time.time()
        urls = db_urls.find()
        for url in urls:
            try:
                new_checksum = crc32(get_data(url['url']))
            except Exception as e:
                await log("Greska prilikom updatovanja strane " + url['url'] + '\n' + str(e))
                continue
            message = ""
            if url['checksum'] != new_checksum:
                has_followers = False
                for ctx in url['ctx']:
                    await client.get_user(int(ctx['id'])).send(messages.page_changed + '\n' + url['url'])
                    await log(ctx['author'] + " je obavesten(a) o promeni " + url['url'])
                db_urls.update_one({"url" : url['url']}, {'$set' : {"checksum" : new_checksum}})
        await log("Strane updatovane za " + "{:.2f}s".format(time.time() - begin_t))

async def prune_db():
    await client.wait_until_ready()
    while not client.is_closed():
        await log("Cistim bazu...")
        try:
            begin_t = time.time()
            db_urls.delete_many({'ctx' : {'$exists' : 'true', '$size' : 0}})
            await log("Baza ociscena za " + "{:.2f}s".format(time.time() - begin_t))
        except Exception as e:
            await log(messages.db_error + '\n' + str(e))
        await sleep(config.prune_period)

async def log(string):
    print(string)
    await client.get_channel(config.log_channel).send(string)

client.loop.create_task(watch())
client.loop.create_task(prune_db())
client.run(config.token)