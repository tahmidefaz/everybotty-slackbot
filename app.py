import logging
import os
import requests
from slack_bolt import App
from slack_sdk.web import WebClient

app = App()

CHATBOT_API_BASEURL = os.environ.get("CHATBOT_API_BASEURL", "")
CHATBOT_AUTH_KEY = os.environ.get("CHATBOT_AUTH_KEY", "")

#{"ts1":{"type":"bot-type", "prompts":["message","response","message"]},}
listening_threads = dict()

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


def is_reply(message) -> bool:
    return message.get("subtype") != "message_replied" and message.get("thread_ts") in listening_threads

@app.event(
    event="message",
    matchers=[is_reply]
)
def handle_reply(logger, event, say):
    msg_ts = event['thread_ts']
    text = event["text"]

    bot_type = listening_threads[msg_ts]["type"]
    prompts = listening_threads[msg_ts]["prompts"]
    prompts.append(text)

    if len(prompts) > 11:
        prompts = prompts[1:]

    formatted_prompts = format_prompts(prompts)

    bot_response = send_prompt(bot_type, formatted_prompts)
    if bot_response:
        prompts.append(bot_response)
        say(text=bot_response, thread_ts=msg_ts)

        listening_threads[msg_ts]["prompts"] = prompts

    print("formatted prompts...", formatted_prompts)


@app.event("app_mention")
def handle_mention(body, say, logger):
    msg_ts = body["event"]["ts"]
    text = body["event"]["text"]
    personalities = get_personalities()
    if not personalities:
        say(f"One of my internal API is down. Sorry, I can\'t respond right now. :sob:")
        return

    formatted_personalities = list(map(lambda x: f"`{x}`", personalities))
    splitted_message = text.split(" ")

    if len(splitted_message) < 2:
        say(f'Usage: `@Everybotty personalities`')
        return

    if len(splitted_message) == 2 and splitted_message[-1] == "personalities":
        say(f'Here are the available personalities:\n{" ".join(formatted_personalities)}\nUsage: `@Everybotty bot-personality`\n')
        return

    bot_personality = splitted_message[1]
    if bot_personality not in personalities:
        say(f'Bot personality, {bot_personality}, does not exist.\nUsage: `@Everybotty bot-personality`\nAvailable personalities:\n{" ".join(formatted_personalities)}')
        return

    say(thread_ts=msg_ts, text=f'You are now talking with {bot_personality}\nReply in this thread to continue the conversation! :robot_face:')
    listening_threads[msg_ts] = {"type":bot_personality, "prompts":[]}

    return


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    port = int(os.environ.get("PORT", "3000"))
    app.start(port)
