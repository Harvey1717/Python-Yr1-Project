import discord
from datetime import datetime
from config import PREFIX, EMBED_COLOR


def add_command(client, **kargs):
    @client.command()
    async def help(ctx):
        # * This command returns a help embed(s) to the user
        embed = discord.Embed()

        embed.title = "Auth Bot | Help"
        embed.description = f"Example Command: {PREFIX}cmd arg1 *arg2*\nArguements in italics are optional arguements"
        embed.add_field(
            name=f"{PREFIX}help", value="Displays this message", inline=False
        )
        embed.add_field(
            name=f"{PREFIX}ping",
            value="Returns 'Pong!'. Used to check if the bot is online",
            inline=False,
        )
        embed.add_field(
            name=f"{PREFIX}auth key",
            value="Only works in direct message with this bot\nAllows a user to claim a key to get specific roles",
            inline=False,
        )
        embed.color = discord.Color(EMBED_COLOR)
        embed.timestamp = datetime.now()

        await ctx.send(embed=embed)

        if ctx.message.author.guild_permissions.administrator:
            # * Chekcs if a user is an administrator, if they are then send both help embeds (Standard & Staff cmds)
            embed = discord.Embed()

            embed.title = "Auth Bot | Admin Help"
            embed.add_field(
                name=f"{PREFIX}help", value="Displays this message", inline=False
            )
            embed.add_field(
                name=f"{PREFIX}generate_keys*",
                value="Starts the generation process",
                inline=False,
            )
            embed.add_field(
                name=f"{PREFIX}lookup_user*",
                value="Looks up a user and returns their info",
                inline=False,
            )
            embed.add_field(
                name=f"{PREFIX}lookup_key*",
                value="Looks up a key and returns it's info",
                inline=False,
            )
            embed.color = discord.Color(EMBED_COLOR)
            embed.timestamp = datetime.now()

            await ctx.send(embed=embed)
