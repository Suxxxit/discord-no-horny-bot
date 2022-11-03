# discord-no-horny-bot

## Purpose
I am not a big fan of moderation, especially done by bots. *Shaming*, on the other hand...

This Discord bot will check all pictures sent to the server where it is installed, and if a picture contains NSFW materials, bot will mention the sender with randomly generated shaming message and will send a random reaction picture.

## Features
- Picture categorization powered by [nsfw-detector](https://pypi.org/project/nsfw-detector/), supporting the following categories:
    - porn
    - sexy
    - hentai
    - drawings
    - neutral
- Additional adjustment for more presice detection
- Different sets of phrases and pictures for scenarios when picture is posted under/without spoiler
- 2-component phrases, allowing more variety in the bot responses
- Channel exclusion for channels where posting lewd stuff is kinda the whole point
- Suitable to be ran on a remote VM

## Quickstart
To create the bot itself, please refer to official [Discord Developer documentation](https://discordpy.readthedocs.io/en/stable/discord.html).

1. Install dependencies:
    ```bash
    python3 -m pip install -U discord.py
    python3 -m pip install -U nsfw-detector
    # if you have low memory, add this parameter: --no-cache-dir
    ```
2. Download a model for image prediction:
    ```bash
    mkdir model
    cd model
    wget https://github.com/GantMan/nsfw_model/releases/download/1.1.0/nsfw_mobilenet_v2_140_224.zip
    unzip nsfw_mobilenet_v2_140_224.zip
    rm nsfw_mobilenet_v2_140_224.zip
    ```
3. In the repo folder, create a `.discordtoken` file and place your bot token there.
4. Add pictures to `pics` folder and add phrases of your liking to text files in `dictionaries` folder.
5. Open `config.json` and set up the bot parameters. You can also check if paths to images and dictionaries are correct.
   **NOTE**: File paths are used by `glob`, so make sure to leave asterisk(`*`) at the end unless you want to use a single file.
6. Authorize the bot on your server by substituting your APP_ID and opening this link:
    `https://discordapp.com/oauth2/authorize?&client_id=APP_ID&scope=bot`
7. [*OPTIONAL*] Create a simple systemd service:
    ```bash
    # edit the path to your Python binary and to the repo
    echo "[Unit]
    Description=Discord no-horny bot

    [Service]
    ExecStart=/usr/bin/python3 /usr/local/etc/discord-no-horny-bot/nohorny.py
    Restart=always
    RestartSec=30

    [Install]
    WantedBy=multi-user.target" > /etc/systemd/system/discord-no-horny.service

    systemctl start discord-no-horny.service
    # check the status and fix the service if something is broken:
    systemctl status discord-no-horny.service

    systemctl enable discord-no-horny.service

    # check the output of the service:
    journalctl -xef -u discord-no-horny
    ```


## Credits
Big gratitude to guys who made [nsfw-detector](https://pypi.org/project/nsfw-detector/), making this project possible without digging into ML land and generating the model from scratch.