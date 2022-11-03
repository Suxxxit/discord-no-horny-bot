import discord
from nsfw_detector import predict
import glob
import random
import requests
import os
import json

curpwd = os.path.realpath(os.path.dirname(__file__))
config_path = f'{curpwd}/config.json'


def read_config(cfg_path):
    with open(cfg_path, 'r') as fd:
        config = json.load(fd)
    
    return config


def predict_image(image_url, forbidden_themes, weight_qualifier, model, pathtowrite):
    img_data = requests.get(image_url).content
    with open(pathtowrite, 'wb') as handler:
        handler.write(img_data)
    result = predict.classify(model, pathtowrite)
    resval = list(result.values())[0]

    if os.path.exists(pathtowrite):
        os.remove(pathtowrite)
    prediction = max(resval, key=resval.get)
    cat_sum = 0
    answer = False

    for theme in forbidden_themes:
        cat_sum = cat_sum + resval[theme]

    if prediction in forbidden_themes or cat_sum >= weight_qualifier:
        answer = True
    else:
        answer = False

    print(  f"Predicted category: {prediction};",
            f"Weight of target categories - {str(cat_sum)}/{str(weight_qualifier)};",
            f"Reaction - {str(answer)}", flush=True)
    
    return answer


def get_dictionaries(dirconf):
    default_dicts = []
    nospoiler_dicts = []
    def_files = glob.glob(f"{curpwd}/{dirconf['prefix']}{dirconf['files_default']}")
    nosp_files = glob.glob(f"{curpwd}/{dirconf['prefix']}{dirconf['files_nospoiler']}")
    def_files.sort()
    nosp_files.sort()

    for fpath in def_files:
        default_dicts.append(read_multiline_to_list(fpath))
    for fpath in nosp_files:
        nospoiler_dicts.append(read_multiline_to_list(fpath)) 
    
    for _ in range(2):  # Safeguard for cases when there is no source files found
        default_dicts.append([''])
        nospoiler_dicts.append([''])

    dicts = {
        'default' : default_dicts,
        'nospoiler' : nospoiler_dicts
    }
    print(  f"== Loaded {len(dicts['default'][0])}+{len(dicts['default'][1])}",
            f"default phrases and {len(dicts['nospoiler'][0])}+{len(dicts['nospoiler'][1])}",
            "no-spoiler phrases")

    return dicts


def read_multiline_to_list(filepath):
    with open(filepath, 'r') as fd:
        filecontent = fd.readlines()
    result = []

    for line in filecontent:
        result.append(line.rstrip())

    return result


def find_images(imgconf):
    def_img = glob.glob(f"{curpwd}/{imgconf['prefix']}{imgconf['files_default']}")
    nosp_img = glob.glob(f"{curpwd}/{imgconf['prefix']}{imgconf['files_nospoiler']}")
    def_img.sort()
    nosp_img.sort()
    images = {
        'default' : def_img,
        'nospoiler' : nosp_img
    }
    print(f"== Loaded {len(images['default'])} default images and {len(images['nospoiler'])} no-spoiler images")

    return images


def main():
    cfg = read_config(config_path)
    with open(f"{curpwd}/{cfg['token_location']}", 'r') as fd:
        token = fd.read().rstrip()
    
    image_dict = find_images(cfg['images'])
    msg_dict = get_dictionaries(cfg['dictionaries'])
    model = predict.load_model(f"{curpwd}/{cfg['model_path']}")

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}', flush=True)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.attachments and message.channel.name not in cfg['excluded_channels']:
            print(f'Analyzing attachment from {message.author.name} in channel {message.channel.name}, flush=True')
            if predict_image(message.attachments[0].url,
                            cfg['blocklist'],
                            cfg['sum_weight_threshold'],
                            model,
                            f'{curpwd}/{cfg["images"]["prefix"]}{cfg["images"]["tempdir"]}{message.attachments[0].filename}'):
                if message.attachments[0].filename.startswith('SPOILER'):
                    print("Image is under SPOILER, responding...", flush=True)
                    await message.channel.send(
                        f"{message.author.mention} {random.choice(msg_dict['default'][0])} {random.choice(msg_dict['default'][1])}!",
                        file = discord.File(random.choice(image_dict['default']))
                        )
                else:
                    print("Image is plainly visible, responding...", flush=True)
                    await message.channel.send(
                        f"{message.author.mention} {random.choice(msg_dict['nospoiler'][0])} {random.choice(msg_dict['nospoiler'][1])}!",
                        file = discord.File(random.choice(image_dict['nospoiler']))
                        )
            else:
                return

    client.run(token)


if __name__ == '__main__':
    main()