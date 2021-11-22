import discord
from discord.ext import commands
import pymongo
import importlib
import asyncio
from harvey_logger import logger

from datetime import datetime
import os
from config import BOT_TOKEN, PREFIX, DB_PASSWORD, SERVER_ID

# Throughout this program you will probably see comments that start like this: # *
# This is because I use a VS Code extension called Better Comments which automatically categorises
# and formats comments in different colours based on what is after the normal comment symbol (#)
# star (*) is used to highlight comments in green which is why I use it a lot

return_def_err_errs = [
    commands.MissingRequiredArgument,
    commands.MissingPermissions,
    commands.NoPrivateMessage,
    commands.CommandNotFound,
]


logger = logger.Logger()  # * Custom logger module I made for colours and time

intents = discord.Intents.default()
intents.members = True

# * Activity shows that bot is playing...
# * Setting client
client = commands.Bot(
    intents=intents,
    command_prefix=PREFIX,
    activity=discord.Game("$help | Python Project"),
)

# * Removes default help command
client.remove_command("help")


async def check_keys():
    """
    ASYNC Checks the key database for expired keys and deletes them then kicks users if it finds any
    """
    try:
        while True:
            logger.logp("Checker", "Checking...")
            key_doc = db_collection.find(
                {"key.expires_at": {"$lte": datetime.utcnow()}}
            )
            for doc in key_doc:
                logger.alertp(
                    f"Checker {doc['_id']}", f"Expired Key -> {doc['key']['key']}"
                )
                if not doc["user"]["discord_id"]:
                    logger.logp(f"Checker {doc['_id']}", "Key not linked. Deleting...")
                else:
                    server = client.get_guild(
                        int(SERVER_ID)
                    )  # * Get guild to check if user is a member of specific server

                    server_member = server.get_member(doc["user"]["discord_id"])
                    if server_member:
                        await server_member.kick()
                        logger.successp(f"Checker {doc['_id']}", "Kicked User")

                db_collection.delete_one({"_id": doc["_id"]})
                logger.successp(f"Checker {doc['_id']}", "Deleted Key")

            await asyncio.sleep(5)
    except Exception as ex:
        print(ex)


@client.event  # * Discord decorator
async def on_ready():
    # * Logs when the bot is connected/ready
    logger.logp("Bot", "Bot Is Ready!")
    # * Check declaration
    asyncio.ensure_future(check_keys())


@client.event
async def on_command_error(ctx, error):
    # * Checks a class instance has a specific attribute
    if hasattr(ctx.command, "name"):
        logger.errorp(
            "Bot",
            f"Failed Command: {ctx.command.name} | {error} | - {ctx.message.content}",
        )
    else:
        logger.errorp(
            "Bot",
            f"Failed Command | {error} | - {ctx.message.content}",
        )
    # * Checks return_def_err_errs for errors that should send the default error message to the user
    if any([isinstance(error, err) for err in return_def_err_errs]):
        await ctx.send(error)
    else:
        await ctx.send(f"Unhandled error. Contact support")
        raise error


def get_db_collection():
    mongo_client = pymongo.MongoClient(
        f"mongodb+srv://harveywoodall:{DB_PASSWORD}@cluster0.uqeg9.mongodb.net/ntu-auth?retryWrites=true&w=majority"
    )
    db = mongo_client["ntu-auth"]  # * DB name
    col = db["keys"]  # * Collection name
    return col


db_collection = get_db_collection()


def add_commands():
    logger.logp("Main", "Starting Command Adder")
    commands_to_add = []
    # * Check declaration
    with os.scandir("commands") as entries:
        for entry in entries:
            if entry.name.endswith(".py"):
                commands_to_add.append(entry.name)

    for cmd_module in commands_to_add:
        cmd_module_name = cmd_module.split(".py")[0]
        # * Check declaration
        cmd_module = importlib.import_module(f"commands.{cmd_module_name}")
        cmd_module.add_command(client, db_collection=db_collection)
        logger.msgp("Main", f"{cmd_module_name.upper()} Command Added!")


add_commands()

client.run(BOT_TOKEN)