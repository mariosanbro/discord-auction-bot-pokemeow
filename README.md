# discord-auction-bot-pokemeow
This bot is an open source Discord bot coded in Python with [Discord.py](https://discordpy.readthedocs.io/en/stable/) by [mariosanbro](https://github.com/mariosanbro).
Feel free to add a star :star: to the repository if you liked it!

# Table of contents
- [Roadmap](#roadmap)
- [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Have the bot running](#have-the-bot-running)
    - [Setup server](#setup-server)
- [License](#license)


# Roadmap
- [x] Basic auction system (auction and bid).
- [x] Autobuy auction.
- [x] Bundle auction.
- [x] Accepted in auction (for different bid methods).
- [ ] Accepted list templates to quick load in auctions.
- [ ] Patreon tokens bid.
- [ ] Trading setup after auction ending.
- [ ] Auction ping roles.
- [ ] Reputation system.
- [ ] Logging system.

More to come...

# Installation
In order to install and have the bot ready first you have to download it (I recommend to always download last version since it will have last features and bugfixes).

## Prerequisites
Before diving into the installation process, you'll need:

- Python 3.10 or later installed on your machine (3.11+ recommended)
- All the necessary dependencies listed in [requirements.txt](https://github.com/mariosanbro/discord-auction-bot/blob/main/requirements.txt).

To install these requirements, run the following commands once you installed Python:
```py
# Upgrade pip to the latest version
python -m pip install -U pip

# Install the required packages
pip install -r requirements.txt
```

## Have the bot running
Once you have everything from the prerequisites done, you're ready to have the bot running.

Go to [Discord Developers Portal](https://discord.com/developers/applications) and create a new application.

Then go to `Bot` section, toggle off `PUBLIC BOT` option to avoid the bot frrom joining other servers by error and toggle on all `Privileged Gateway Intents (PRESENCE, SERVER MEMBERS & MESSAGE CONTENT)`.

Once you set up the bot and its intents in the Developers Portal, you have to generate the invite link. Go to `OAuth2` section and in `OAuth2 URL Generator` mark `applications.commands` and `bot`, once you marked bot a new menu will appear (this one with bot permissions). In bot permissions you have to mark `Manage Roles`, `Manage Channels`, `Manage Expressions`, `Create Expressions`, `Send Messages`, `Manage Messages` and `Manage Threads`. Once done you can copy the `Generated URL` below and use it to add the bot to your server.

The next is go back to `Bot` section and click in `Reset Token` to get your new bot token (save it and keep it safe, it's important).

Now you have to setup a `.env` file in the project directory and add a key with your discord token as follows: `DISCORD_TOKEN = token_here`.

The last step to have the bot running is in the project directory run in the cmd `python -m src.bot.main` to run the bot.

Congratulations, the bot is ready to use and running.

## Setup server
Now that the bot is running you only need to setup `auctions`, `auction info` and `trading` categories.

Once you set them be sure that you have minimum 12 emoji slots free (since the next step will create emojis and channels in the server).

Last step is as easy as run the command `/setup`, this command will create the emojis needed by the bot and the channels needed (you will be able to personalize the name from the channels later).

And done!, now you can run in auctions!

# Links
If you have any question feel free to join the discord server, I'll try to reply and help.
- [Discord Server](https://discord.gg/QVW53Wtpc4)

# License
Discord Auction Bot is licensed under the GPL 3.0 license. See the file `LICENSE` for more information. If you plan to use any part of this source code in your own bot, I would be grateful if you would include some form of credit somewhere.
