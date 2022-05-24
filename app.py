import logging
import os
import requests
from slack_bolt import App
from slack_sdk.web import WebClient

app = App()

CHATBOT_API_BASEURL = os.environ.get("CHATBOT_API_BASEURL", "")
CHATBOT_AUTH_KEY = os.environ.get("CHATBOT_AUTH_KEY", "")


def get_personalities():
    response = requests.get(f"{CHATBOT_API_BASEURL}/personalities")
    if response.status_code != 200:
        return None

    response_json = response.json()

    return [p["id"] for p in response_json]

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
    print("gpt2 chatbot response...", response.content)
    return response_json['response']

@app.event("app_mention")
def handle_mention(body, say, logger):
    user = body["event"]["user"]
    text = body["event"]["text"]

    personalities = get_personalities()
    if not personalities:
        say(f"One of my internal API is down. Sorry, I can\'t respond right now. :sob:")
        return

    formatted_personalities = list(map(lambda x: f"`{x}`", personalities))
    splitted_message = text.split(" ")

    if len(splitted_message) == 2 and splitted_message[-1] == "personalities":
        say(f'Here are the available personalities:\n{" ".join(formatted_personalities)}\nUsage: `bot-personality your message`\n')
        return

    bot_personality = splitted_message[1]
    if bot_personality not in personalities:
        say(f'Bot personality, {bot_personality}, does not exist.\nUsage: `bot-personality your message`\nAvailable personalities:\n{" ".join(formatted_personalities)}')
        return

    prompt = " ".join(splitted_message[2:])
    if len(prompt) > 0:
        bot_response = send_prompt(bot_personality, prompt)
        logger.info(bot_response)
        if bot_response:
            say(bot_response)

    logger.info(body)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.start(3000)
