from os import environ, path


class Settings:
    token = environ['TOKEN']
    watching_channel_id = int(environ['VOICE_CHANNEL'])
    category_channel_id = int(environ['CATEGORY_CHANNEL']) if 'CATEGORY_CHANNEL' in environ else None
    user_limit = int(environ['USER_LIMIT']) if 'USER_LIMIT' in environ else None
    channels_filename = 'channels.txt'


def get_watching_channels():
    if not path.exists(Settings.channels_filename):
        return []

    with open(Settings.channels_filename) as f:
        channels = f.read()
        return [
            int(channel)
            for channel in channels.split(',')
            if channel
        ]


def _save_watching_channels():
    with open(Settings.channels_filename, 'w') as f:
        f.write(','.join(map(str, watching_channels)))


def add_watching_channel(channel_id):
    watching_channels.append(channel_id)
    _save_watching_channels()


def delete_watching_channel(channel_id):
    watching_channels.remove(channel_id)
    _save_watching_channels()


watching_channels: list = get_watching_channels()
