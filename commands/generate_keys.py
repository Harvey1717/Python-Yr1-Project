from discord.ext import commands
from datetime import datetime, timedelta
import random
from harvey_logger import logger
from modules.get_key_embed import get_key_embed
from config import SERVER_ID
import asyncio

logger = logger.Logger()


def get_ran_string(length=4):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    return "".join([random.choice(characters) for _ in range(0, 4)])


def gen_key(prefix):
    return f"{prefix}-{'-'.join([get_ran_string() for _ in range(0, 3)])}"


def get_key(db_col, prefix="NTU"):
    key = gen_key(prefix)
    if db_col.find_one({"key.key": key}):
        get_key(prefix)
    else:
        return key


def check(ctx, channelID, authorID):
    return ctx.message.channel.id == channelID and ctx.message.author.id == authorID


def add_command(client, **kargs):
    @client.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def generate_keys(ctx, *args):
        db_col = kargs["db_collection"]
        channelID = ctx.message.channel.id
        authorID = ctx.message.author.id

        def check(msg):
            return msg.channel.id == channelID and msg.author.id == authorID

        await ctx.send(
            "**Starting Key Generation...**\nI will now ask you a series of questions which you must respond to within 30 seconds per question otherwise the generation process will exit"
        )

        # * Ask user for key prefix
        await ctx.send("Enter a key prefix, type N for default")
        msg = await client.wait_for("message", check=check, timeout=30)
        if msg.content.lower() == "n":
            prefix = False
        elif len(msg.content) > 0:
            prefix = msg.content
        else:
            return await ctx.send("Error: process exiting, please use command again")

        # * Ask user for key amount
        await ctx.send("How many keys do you want to generate?")
        msg = await client.wait_for("message", check=check, timeout=30)
        try:
            keys_amount = int(msg.content)
        except Exception as ex:
            return await ctx.send("Error: process exiting, please use command again")

        # * Ask user for role IDs to add
        await ctx.send(
            "Please enter the role IDs (seperated by a comma) to add to the user who claims this key\nE.g 785134095839002624"
        )
        msg = await client.wait_for("message", check=check, timeout=30)
        if len(msg.content) > 0:
            roles = msg.content.split(",")
        else:
            return await ctx.send("Error: process exiting, please use command again")

        # * Ask user for key expiry
        await ctx.send(
            "How many days do you want this key to last for?\nN for never or number of days"
        )
        msg = await client.wait_for("message", check=check, timeout=30)
        if msg.content.lower() == "N":
            expires_days = False
        elif int(msg.content) > 0:
            expires_days = int(msg.content)
        else:
            return await ctx.send("Invalid response")

        keys = []

        for i in range(0, keys_amount):
            if prefix:
                keys.append(get_key(db_col, prefix))
            else:
                keys.append(get_key(db_col))

        send_single_embeds = len(keys) <= 10

        for key in keys:
            doc = {
                "key": {
                    "key": key,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(expires_days),
                    "claimed_at": None,
                    "roles": roles,
                },
                "user": {
                    "discord_id": None,
                    "discord_tag_on_auth": None,
                },
            }
            x = db_col.insert_one(doc)
            logger.successp(
                "Bot", f"Added New Key! -> {doc['key']['key']} | {x.inserted_id}"
            )
            if send_single_embeds:
                await ctx.send(embed=get_key_embed(doc))

        if not send_single_embeds:
            await ctx.send("More than 10 keys, sending all at once")

        if len(keys) > 1:
            await ctx.send("\n".join(keys))