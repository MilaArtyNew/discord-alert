# discord-monitor

Мониторинг Discord каналов → уведомления в Telegram.
Self-bot на отдельном Discord-аккаунте.

## Получить Discord User Token

1. Открыть Discord в браузере (discordapp.com)
2. F12 → Network → фильтр `api`
3. Обновить страницу, найти любой запрос к `discord.com/api`
4. Headers → Authorization → скопировать значение (без "Bearer")

Или через Console:
```js
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```

## Получить Channel ID

1. Discord → Settings → Advanced → Developer Mode: ON
2. ПКМ на канале → Copy Channel ID

## Установка

```bash
cd /home/gpt/discord-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # заполнить
```

## Тест запуска

```bash
source venv/bin/activate
python bot.py
```

## Деплой как systemd

```bash
sudo cp deploy/systemd/discord-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-monitor
sudo systemctl start discord-monitor
sudo journalctl -u discord-monitor -f
```
