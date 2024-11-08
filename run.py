import discord
from aiohttp import BasicAuth

from utils import Settings, watching_channels, add_watching_channel, delete_watching_channel


def get_client():
    options = {}
    if Settings.discord_proxy_url:
        options['proxy'] = Settings.discord_proxy_url
        options['proxy_auth'] = BasicAuth(Settings.discord_proxy_login, Settings.discord_proxy_password)

    return discord.Client(intents=discord.Intents(guilds=True, voice_states=True), **options)


client = get_client()


async def create_new_channel(member: discord.Member, guild: discord.Guild):
    for category_id in Settings.category_channel_ids:
        category = guild.get_channel(category_id)
        try:
            new_channel: discord.VoiceChannel = await guild.create_voice_channel(
                member.display_name,
                user_limit=Settings.user_limit,
                category=category
            )
            break
        except discord.errors.HTTPException as e:
            if e.status != 400 or e.code != 50035:
                raise
    add_watching_channel(new_channel.id)
    print(f'creating new channel {new_channel.id}')
    try:
        await member.move_to(new_channel)
    except discord.errors.HTTPException:
        await delete_channel_if_empty(new_channel)
        raise
    await new_channel.set_permissions(member, manage_channels=True)


async def delete_channel_if_empty(channel: discord.VoiceChannel):
    try:
        channel = await client.fetch_channel(channel.id)
    except discord.errors.NotFound:
        return
    if channel and not len(channel.members):
        print(f'deleting old channel {channel.id}')
        await channel.delete()
        delete_watching_channel(channel.id)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    for channel_id in watching_channels:
        channel: discord.VoiceChannel = client.get_channel(channel_id)
        if channel is None:
            delete_watching_channel(channel_id)
        else:
            await delete_channel_if_empty(channel)


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel == after.channel:
        return

    if before.channel is not None and before.channel.id in watching_channels:
        print(f'leaving old channel {before.channel.id}')
        await delete_channel_if_empty(before.channel)

    if after.channel is not None and after.channel.id == Settings.watching_channel_id:
        await create_new_channel(member, after.channel.guild)


client.run(Settings.token)
