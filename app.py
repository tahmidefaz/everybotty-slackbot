import logging
import os
import re
import requests
from slack_bolt import App
from slack_sdk.web import WebClient

from blocks import get_personality_blocks, get_commands_block

app = App()

CHATBOT_API_BASEURL = os.environ.get("CHATBOT_API_BASEURL", "")
CHATBOT_AUTH_KEY = os.environ.get("CHATBOT_AUTH_KEY", "")

#{"ts1":{"type":"bot-type", "prompts":["message","response","message"]},"extra":{"icon_emoji": ":something:"}}
listening_threads = dict()

def get_personalities():
    response = requests.get(f"{CHATBOT_API_BASEURL}/personalities")
    if response.status_code != 200:
        return None

    return response.json()

def check_personality(available_personality, personality):
    if not available_personality:
        return False
    if personality not in available_personality:
        return False
    return True

def send_prompt(personality, prompt):
    response = requests.post(f"{CHATBOT_API_BASEURL}/chat",
        params={"personality": personality, "prompt":prompt},
        headers={"Authorization": CHATBOT_AUTH_KEY})
    
    if response.status_code != 200:
        return None
    
    response_json = response.json()
    return response_json['response']

def format_prompts(prompts):
    prompt_string = ""
    for i, prompt in enumerate(prompts):
        if i == 0:
            prompt_string += prompt
        elif i%2 != 0:
            prompt_string += f"\nResponse: {prompt}"
        else:
            prompt_string += f"\nMessage: {prompt}"
    return prompt_string


def get_bot_info(bot_personality, bots_info):
    for bot in bots_info:
        if bot["id"] == bot_personality:
            return bot


def is_reply(message) -> bool:
    return message.get("subtype") != "bot_message" and message.get("thread_ts") in listening_threads

@app.event(
    event="message",
    matchers=[is_reply]
)
def handle_reply(logger, event, say, body):
    msg_ts = event['thread_ts']
    text = event["text"]

    bot_type = listening_threads[msg_ts]["type"]
    bot_name = listening_threads[msg_ts]["name"]
    extra_configs = listening_threads[msg_ts]["extra"]
    prompts = listening_threads[msg_ts]["prompts"]
    prompts.append(text)

    if len(prompts) > 11:
        prompts = prompts[2:]

    formatted_prompts = format_prompts(prompts)

    bot_response = send_prompt(bot_type, formatted_prompts)
    if bot_response:
        prompts.append(bot_response)
        say(text=bot_response, thread_ts=msg_ts, username=bot_name, **extra_configs)

        listening_threads[msg_ts]["prompts"] = prompts

    print("formatted prompts...", formatted_prompts)


@app.event("app_mention")
def handle_mention(body, say, logger):
    if "thread_ts" in body["event"]:
        say(text="Sorry, I have no power here. Please send a new message to the channel.", thread_ts=body["event"]["thread_ts"])
        return

    msg_ts = body["event"]["ts"]
    text = body["event"]["text"].lower()
    bots_info = get_personalities()

    blocks = get_personality_blocks(bots_info)
    block_elements = blocks["blocks"]

    personalities = [p["id"] for p in bots_info]
    if not personalities:
        say(f"One of my internal API is down. Sorry, I can\'t respond right now. :sob:")
        return

    regex_string = "\\b(help|commands|personalities|" + "|".join(personalities)+")\\b"
    matches = re.findall(regex_string, text)

    if len(matches) < 1:
        say("", blocks=block_elements)
        return

    first_match = matches[0]

    if first_match == "personalities":
        say("", blocks=block_elements)
        return

    if first_match == "help" or first_match == "commands":
        say("", blocks=get_commands_block())

    bot_personality = first_match

    bot_info = get_bot_info(bot_personality, bots_info)

    say(thread_ts=msg_ts, text=f'You are now talking with {bot_info["name"]}\n{bot_info["description"]}\nReply in this thread to continue the conversation! :robot_face:')
    listening_threads[msg_ts] = {"type":bot_info["id"], "name": bot_info["name"], "prompts":[], "extra": bot_info["slack_config"]}

    return


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    port = int(os.environ.get("PORT", "3000"))
    app.start(port)
