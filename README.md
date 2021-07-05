# TG-Bot for writing, monitoring, completing tasks

## Install and setup application

**bash**
```
cd ~/.
git clone https://github.com/shaggy-axel/monitoring_tasks_bot.git
cd monitoring_tasks_bot/
touch .env
```
**.env**
```
TG_TOKEN=<telegram_bot_token>
POSTGRES_DB=database_name
POSTGRES_USER=database_user
POSTGRES_PASSWORD=database_password
```
**bash**
```
docker-compose up -d
```

## Get your bot token from BotFather
- Click -> [@BotFather](https://t.me/botfather)
- Send him the command:
     `/newbot`
- Follow the instructions
