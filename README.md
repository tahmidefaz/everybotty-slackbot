# Requirements

* python >= 3.7
* [Internal Api](https://github.com/CodyWMitchell/GPT3-Chatbot-API)

# Setting up the slack bot

## Initializing the slack bot server

### Environment variable setup
```
SLACK_BOT_TOKEN = 'x0xb-xxxxxxxxx'                 #Bot User OAuth Token provided by slack
SLACK_SIGNING_SECRET = 'xxxxxxxxx'                 #SlackApp signing secret provided by slack
CHATBOT_API_BASEURL = 'https://example.com/api'    #BaseURL of the internal API
CHATBOT_AUTH_KEY = 'xxxxxxx'                       #Api access key provided by the internal API
```
###  Startup
```
pip install -r requirements.txt

python3 app.py
```

### Deployment
You can use the above steps to deploy the slackbot anywhere.
We have only tried the cloud deployment with [heroku](https://www.heroku.com/) and local deployment with [ngrok](https://ngrok.com/). A heroku Procfile is provided for your convenience.


## Slack App configurations

#### OAuth & Permissions

You will the the following OAuth Scopes as the Bot Token Scopes

* `app_mentions:read`
* `channels:history`
* `chat:write`
* `chat:write.customize`

#### Event Subscriptions

You will need to enable events subscriptions for your slack bot.

* Point to the correct request URL for the events where your bot server is set up. Don't forget to append `/slack/events` at the end.
* Subscribe to the following "bot events":
  * `app_mention`
  * `message.channels`

That should be all you need. Install the app in a slack workspace, add it to a channel and do `@<your-bot-name>`. Enjoy. 🤖


### Bot Commands

* Show available personalities
  * `@Everybotty`
  * `@Everybotty personalities`
* Talk with a specific chatbot
  * `@Everybotty <bot-personality>`
