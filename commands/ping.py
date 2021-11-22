def add_command(client, **kargs):
    @client.command()
    async def ping(ctx):
        # * This command can be used to chcek the bot is up and running
        await ctx.send("Pong!")