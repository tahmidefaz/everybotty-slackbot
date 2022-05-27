
def get_context_block(bot_id, description, icon_url=None, icon_emoji=None):
    context = {"type": "context"}
    elements = []

    text_element = dict()
    text_element["type"] = "mrkdwn"

    if icon_url:
        elements.append({"type": "image", "image_url": icon_url, "alt_text": bot_id})
        text_element["text"] = f"*{bot_id}* - {description}"
    elif icon_emoji:
        text_element["text"] = f"{icon_emoji} *{bot_id}* - {description}"

    elements.append(text_element)
    context["elements"] = elements

    return context


def get_personality_blocks(personalities):
    template = {"blocks":[{ "type": "section", "text": {"type": "mrkdwn", "text": "*Here are your personality options:*" }},{"type": "divider"}]}

    for bot in personalities:
        template["blocks"].append(get_context_block(bot["id"],bot["description"],**bot["slack_config"]))
    
    footers = [{"type": "divider"}, {"type": "context", "elements": [{"type": "mrkdwn", "text": "Example: *@Everybotty gaga-bot*"}]}]
    template_blocks = template["blocks"]

    template["blocks"] = [*template_blocks, *footers]

    return template


def get_commands_block():
    return [{ "type": "section", "text": { "type": "mrkdwn", "text": "*Here are the available bot commands* :robot_face: :boom:" }},{"type": "divider"},{"type": "section","text": {"type": "mrkdwn","text": "Show the available personalities:\n```@Everybotty```\n```@Everybotty personalities```"}},{"type": "section","text": {"type": "mrkdwn","text": "Talk to one of the chatbots:\n```@Everybotty bot-personality```"}},{"type": "section","text": {"type": "mrkdwn","text": "Show this message:\n```@Everybotty commands```\n```@Everybotty help```"}}]
