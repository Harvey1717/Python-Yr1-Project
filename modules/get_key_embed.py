from discord import Embed, Color
from datetime import datetime
from config import EMBED_COLOR


def get_key_embed(key_doc):
    embed = Embed()

    embed.title = "Auth Bot | Key Info"
    embed.add_field(name="Key", value=key_doc["key"]["key"], inline=False)
    embed.add_field(
        name="Expires (UTC)", value=key_doc["key"]["expires_at"], inline=False
    )
    embed.add_field(
        name="Created At (UTC)", value=key_doc["key"]["created_at"], inline=False
    )
    embed.add_field(
        name="Claimed At (UTC)", value=key_doc["key"]["claimed_at"], inline=False
    )
    embed.add_field(
        name="Roles",
        value=", ".join(f"<@&{role}>" for role in key_doc["key"]["roles"]),
        inline=False,
    )
    embed.add_field(
        name="User", value=f"<@{key_doc['user']['discord_id']}>", inline=False
    )
    embed.color = Color(EMBED_COLOR)
    embed.timestamp = datetime.now()

    return embed