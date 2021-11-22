from config import SERVER_ID
from datetime import datetime
import discord.utils
from harvey_logger.logger import Logger

logger = Logger()


class Authenticator:
    def __init__(self, client):
        self.client = client

    def set_server(self, server_id):
        """
        Sets the server attribute

        Parameters:
            server_id (int/string): A Discord server ID
        """
        self.server = self.client.get_guild(int(server_id))

    def set_server_member(self, user_id):
        """
        Sets and checks whether a user is in the server

        Parameters:
            user_id (int/string): A Discord user ID

        Returns:
        bool: Whether or not the set member is valid
        """
        self.server_member = self.server.get_member(user_id)
        return bool(self.server_member)

    def set_db_col(self, db_col):
        """
        Sets the db_col attribute
        """
        self.db_col = db_col

    def set_key(self, key):
        """
        Sets the key attribute
        """
        self.key = key

    def check_key(self):
        """
        Checks key and sets key_doc attribute if key is valid

        Returns:
        bool: Whether or not a key is valid i.e. has been claimed or is not an actual key
        """
        key_doc = self.db_col.find_one({"key.key": self.key})
        if not key_doc or key_doc["key"]["claimed_at"]:
            return False  # * Key has expired or claimed so returning False for valid = False
        else:
            self.key_doc = key_doc
            return True

    def check_user_keys(self):
        """
        Returns:
        bool: Whether or not the set member (user) has already claimed a key
        """
        key_doc = self.db_col.find_one({"user.discord_id": self.server_member.id})
        return bool(key_doc)

    def update_key_doc(self):
        """
        Updates (claims a key) a key doc with authenticated users information

        Returns:
        bool: Whether the update was successful
        """
        res = self.db_col.update_one(
            {"key.key": self.key},
            {
                "$set": {
                    "key.claimed_at": datetime.utcnow(),
                    "user.discord_id": self.server_member.id,
                    "user.discord_tag_on_auth": self.server_member.name,
                }
            },
        )
        return bool(res.modified_count > 0)

    async def assign_roles(self):
        """
        ASYNC Assigns roles to a server member

        Returns:
        list: Roles added to server member
        """
        roles_added = []
        for roleID in self.key_doc["key"]["roles"]:
            role = discord.utils.get(self.server.roles, id=int(roleID))
            await self.server_member.add_roles(role)
            roles_added.append(role.name)
        return roles_added


def add_command(client, **kargs):
    @client.command()
    async def auth(ctx, key):
        authenticator = Authenticator(client)
        authenticator.set_server(SERVER_ID)

        valid = authenticator.set_server_member(ctx.message.author.id)
        if not valid:
            return await ctx.send(
                f"You are not a member of {server.name} so you cannot use this command"
            )

        # * If user is a member of specific server
        authenticator.set_db_col(kargs["db_collection"])
        authenticator.set_key(key)
        valid = authenticator.check_key()
        if not valid:
            return await ctx.send("This key has already been claimed or has expired")

        is_authenticated = authenticator.check_user_keys()
        if is_authenticated:
            return await ctx.send("There is already a key associated with your account")

        success = authenticator.update_key_doc()
        if success:
            logger.logp("Bot", f"Key Claimed -> {key} | {ctx.message.author.name}")
            await ctx.send("**YOU HAVE CLAIMED THIS KEY**")
            roles_added = await authenticator.assign_roles()
            if not roles_added:
                await ctx.send("An error occured trying to set all your roles")
            for role in roles_added:
                await ctx.send(f"Assigned {role}")
        else:
            return await ctx.send("An error occured when updating the database")