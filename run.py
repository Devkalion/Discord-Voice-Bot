import discord

from utils import Settings, watching_channels, add_watching_channel, delete_watching_channel

client = discord.Client()


async def create_new_channel(member: discord.Member, guild: discord.Guild):
    category = guild.get_channel(Settings.category_channel_id)
    new_channel: discord.VoiceChannel = await guild.create_voice_channel(
        member.display_name,
        user_limit=Settings.user_limit,
        category=category
    )
    print(f'creating new channel {new_channel.id}')
    await member.move_to(new_channel)
    add_watching_channel(new_channel.id)
    await new_channel.set_permissions(member, manage_channels=True)


async def delete_channel_if_empty(channel: discord.VoiceChannel):
    if not len(channel.members):
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
