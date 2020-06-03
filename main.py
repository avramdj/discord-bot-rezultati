import discord
import pymongo
import config
from util import *
from discord.ext import commands
from asyncio import sleep
import time
import messages

client = commands.Bot(command_prefix='sudo ')
mongo_client = pymongo.MongoClient(config.dbURI)
db = mongo_client[config.dbNAME]
db_urls = db['urls']
db_users = db['users']
channels = []
client.remove_command('help')

@client.event
async def on_ready():
    print("Im ready!")
    activity = discord.Activity(name='MATF', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity, status=discord.Status.idle)

""" @client.event
async def  """

@client.command(name='prati', pass_context=True)
async def prati(ctx, *args):
    if len(args) == 0:
        await ctx.send(messages.need_url)
        return

    url = args[-1].strip('/')

    if not is_valid_url(url):
        await ctx.send(messages.invalid_url)
        return

    if not is_static_url(url):
        await ctx.send(messages.not_static)
        return

    data = get_data(url)
    query = db_urls.find_one({'url' : url})

    if query is not None:
        for ctxx in query['ctx']:
            if ctxx['author'] == str(ctx.author):
                await ctx.send(f'{ctx.author.mention} {messages.already_following}')
                return

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
    except Exception:
        await ctx.send(f'{messages.db_error}')
        return

    await ctx.send(f'{ctx.author.mention} {messages.success_follow}')

@client.command(name='otprati')
async def otprati(ctx, *args):
    if len(args) == 0:
        await ctx.send(messages.need_url)
        return

    if args[-1].strip() == 'sve':
        db_urls.update_many({}, {'$pull' : {
            'ctx' : {
                'author' : str(ctx.author)
            }
        }}) 
        try:
            db_users.update_one({'id' : ctx.author.id} , {'$set' : {'urls' : []}})
        except:
            await ctx.send(f'{messages.db_error}')
            return
        await ctx.send(f'{ctx.author.mention} {messages.success_unfollow}')
        return
    else:
        url = args[-1].strip('/')
        db_urls.update_one({"url": url}, {'$pull' : {
            'ctx' : {
                'author' : str(ctx.author)
            }
        }})
        try:
            db_urls.update_one({"url": url}, {'$pull' : {
                'ctx' : {
                    'author' : str(ctx.author)
                }
            }})
            db_users.update_one({'id' : ctx.author.id}, {'$pull' : { 'urls' : url }})
        except:
            await ctx.send(f'{messages.db_error}')

        await ctx.send(f'{ctx.author.mention} {messages.success_unfollow}')

@client.command(name='strane')
async def strane(ctx, *args):
    user_entry = db_users.find_one({'id' : ctx.author.id})
    message = str(ctx.author.mention) + " "
    if user_entry is None or len(user_entry['urls']) == 0:
        await ctx.send(f'{str(ctx.author.mention)} {messages.following_zero}')
        return
    for url in user_entry['urls']:
        message += "<" + url + ">" + "\n"
    await ctx.send(message)

@client.command(name='sve')
async def sve(ctx, *args):
    urls = db_urls.find({})
    message = "Sve strane u bazi:\n"
    exists = False
    for url in urls:
        message += "<" + url['url'] + ">" + "\n"
        exists = True
    if not exists:
        await ctx.send(f'{str(ctx.author.mention)} {messages.no_pages}')
    else:
        await ctx.send(message)

@client.command(name='help')
async def _help(ctx):
    message = ctx.author.mention + " "
    message += messages.command_list
    await ctx.send(message)
    
""" @client.command(name='educate')
async def spam(ctx, user : discord.User, count):
    for i in range(int(count)):
        await ctx.send(f'{user.mention} kosowo je srb ! ! ! ! ! 1 11 1')
        await sleep(0.5)
 """
async def watch():
    await client.wait_until_ready()
    print("Watching")
    while not client.is_closed():
        urls = db_urls.find()
        for url in urls:
            new_checksum = crc32(get_data(url['url']))
            message = ""
            if url['checksum'] != new_checksum:
                has_followers = False
                for ctx in url['ctx']:
                    await client.get_user(int(ctx['id'])).send(messages.page_changed + '\n' + url['url'])
                db_urls.update_one({"url" : url['url']}, {'$set' : {"checksum" : new_checksum}})
        await sleep(config.sleep_duration)

async def prune_db():
    await client.wait_until_ready()
    print("Cleaning db")
    while not client.is_closed():
        db_urls.delete_many({'ctx' : {
            '$exists' : 'true',
            '$size' : 0
        }})
        await sleep(config.prune_period)

client.loop.create_task(watch())
client.loop.create_task(prune_db())
client.run(config.token)