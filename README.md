[![DockerHub](https://img.shields.io/badge/Docker-Hub-%23099cec?style=for-the-badge&logo=docker)](https://hub.docker.com/r/piratify/discord_donation_bot)
![Docker Pulls](https://img.shields.io/docker/pulls/piratify/discord_donation_bot?color=099cec&style=for-the-badge)

Discord Donation Bot 
=================

This is a chatbot that enables donations on discord via Cashapp or Venmo. 

### Features

- Ability to accept payments from Cashapp or Venmo.  
- Fully automatic chatbot. 

Commands: 
```
.donate
This command is used to start the donation process for a user. 
.setprice <price>
This command is used to set/change price of donation. 
.setrole <@role>
This command is used to  set/change role of donation. 
.setpayment <cashapp/venmo> <address>
This command is used to  set/change address of payment method.
```

# How does it work?
Once the user sends payment including a unique identifying note, the bot then checks email to verify if the note and payment amount matches and then it grants a role to the user. 

<img src="https://github.com/Sleepingpirates/Discord-Donation-Bot/blob/main/Screenshots/example.gif">

# Setup 

**1. Fill out config.json**

Follow guide to setup everything properly. (Important)

[Click here for the full setup guide.](https://github.com/Sleepingpirates/Discord-Donation-Bot/wiki/Configuration)

**Example config.json**

```
{
    "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "role": "donator",
    "Price": 10,
    "cashapp": "test",
    "venmo": "test",
    "note":"1a001-",
    "user":"test@gmail.com",
    "password":"vaadsgagcqlgzsox",
    "imap_url":"imap.gmail.com"
}
```

# Start 

1. Install requirements
```
pip3 install -r requirements.txt 
```
2. Start the bot
```
python3 Run.py
```

# Docker Setup & Start

1. First pull the image 
```
docker pull piratify/discord_donation_bot:latest
```
2. Make the container 

```
docker run -e "token=" -e "user=" -e "pass=" -e "imap_url=" -d --restart unless-stopped --name ddb piratify/discord_donation_bot:latest
```

OR

```
docker run -v /path to config:/app/config.json -d --restart unless-stopped --name ddb piratify/discord_donation_bot:latest
```
