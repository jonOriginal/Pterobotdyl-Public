
# Pterobotdyl - Public
 
 Discord bot for client control for pterodactyl. 
Due to the project being in alpha, there may be bugs that I have not caught, feel free to message me on discord at 12340#0567, or submit and issue or pull request.

### Features
✅ in-chat console
✅ power control
✅ backup management
Planned:
❔File manager
❔Panel Administrator mode

 ### Dependancies:
 - Python 3.7 - 3.10

 -```pip install -r requirements.txt```

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

5. invite the bot to the discord server you will be using. Create a channel where the bot will only be accessable to administrators. 
Bot permissions:
- manage channels 
- send messages, manage messages, embed links, read message history, use slash commands

6. Register the bot with /register, enter your pterodactyl api key, then select the server you will be managing.
### Usage

- do ```/register ``` in the discord channel the bot will be used in. Administrators can only run this. You will have to enter your pterodactyl api key.

- ```/deregister``` to reset api key and server selection.

- ```/power``` to turn off, start, and restart your server.

- ```/backup manage``` to delete and download backups.

- ```/backup create``` to create a new backup.

- messsages starting with ```/``` will be sent to the server as commands.

### Optional
Adding the program as a service:
- cd into the program directory
- run ```nano pterobotdyl.service```
- change the ```WorkingDirectory``` to the path of the program
- change ```ExecStart``` to the path to the main.py file
- run ```sudo mv pterobotdyl.service /etc/systemd/system/pterobotdyl.service``` then ```sudo systemctl daemon-reload```
- enable the service with ```sudo systemctl enable pterobotdyl.service``` 
- start the service with ```sudo systemctl start pterobotdyl.service```
