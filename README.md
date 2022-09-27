
# Pterobotdyl - Public
 Pterodactyl client discord bot
 
 Discord bot for client control for pterodactyl.
 ### Dependancies:
 - Python 3.7 - 3.10

- Pycord
	```pip install py-cord```

- Pydactyl
	```pip install py-dactyl```

- Websockets
	```pip install websockets```

- Requests
	```pip install requests```

### Preparation:
- You need to have a discord application created at [Discord Developer Portal — My Applications](https://discord.com/developers/applications). You will need to enable message intents.

- You will need to have an api key for your pterodactyl server.


### Installation:
1. clone the repository with
	```https://github.com/jonOriginal/Pterobotdyl-Public.git```

2. rename example.env to .env
	```mv example.env .env```
	
3. edit the .env file to include your bot discord token and panel address
	```nano .env```
	
4. start the bot
	```python3 main.py```

### Usage

Invite the bot to the discord server you will be using. Create a channel where the bot will only be accessable to administrators. 
Bot permissions:
- manage channels 
- send messages, manage messages, embed links, read message history, use slash commands

Register the bot with /register, enter your pterodactyl api key, then select the server you will be managing
