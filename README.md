# discord-lobby-bot

This Discord Bot is intended to provide lobby information via voice chat for various games as well as looking up statistics.
It is currently a work in progress and only provides PUBG player stats for Steam players.
There is an audio component, but aside from being able to tell the bot what to speak, there are no automated announcements yet.

## Dependencies

* [FFmpeg](https://www.ffmpeg.org/) - For sending audio to Discord voice channels
* [Python](https://www.python.org/) - This requires at least Python v3
    * Python libaries are listed in the [requirements.txt](requirements.txt) file
    * **python-dotenv** - Convenience for getting environmental variables from a file
    * **discord.py[voice]** - The Discord API Python wrapper with voice capabilities
    * **gTTS** - The Google Text to Speach Python wrapper
    * **pubg-python** - The PUBG API Python wrapper

## Usage

In order to use this bot, you must have a [Discord Bot token](https://discord.com/developers/applications) as well as a [PUBG API token](https://developer.pubg.com/apps).
In Discord, the Members intent must be enabled for the Bot.

The tokens can either be placed in a .env file or set as environmental variables:

* **BOT_TOKEN** - The Discord Bot token
* **PUBG_TOKEN** - The PUBG API token

### Running Locally

If this is running directly on a machine with all the appropreate libraries and environmental variables or files, use `python src/bot.py` 

### Running in Docker

This bot can also be simply run using the pre-built docker image:

* With `.env` file - `docker run -d --env-file .env --name lobby-bot archmageinc/lobby-bot` 
* With passed env vars - `docker run -d -e BOT_TOKEN=MySuperSecretTokenThatIShouldNeverShare -e PUBG_TOKEN=AnotherSecretTokenThatIShouldNeverShare --env-file .env --name lobby-bot archmageinc/lobby-bot`

## Discord Commands

Once the Bot is joined to your Server/Guild, the following commands are currently available:

* **`!join`** - This forces the Bot to join the voice channel you are currently connected to.
* **`!play <text>`** - This will have the Bot speak whatever `<text>` is supplied in the voice channel you are currently connected to.
* **`!leave`** - This will have the Bot leave the voice channel it is connected to.
* **`!stats <PUBG Player Name>`** - This will have the Bot fetch statistics for the PUBG Player. *Player Names are case sensitive*.

## Notes

Since PUBG Seasons change only every so often, the Bot will cache PUBG season data to a file. It will check for updates every 15 days by default.

### Optional Environmental Variables

* **SEASONS_FILE** - The file name for the PUBG cached season data. (*default:* seasons.dat)
* **SEASON_DATA_EXPIRE_DAYS** - The number of days to expire the local cached PUB season data. (*default:* 15 days)
* **TMP_AUDIO_FILE** - The file name of the temporary audio file used for text-to-speech. (*default:* voice.mp3)