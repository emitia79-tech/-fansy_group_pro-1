# Выкладка проекта Fansy на сервер

Ключ OpenAI **не** кладите в репозиторий. Задавайте его переменной окружения **OPENAI_API_KEY** на сервере или в панели хостинга.

---

## Вариант 1. Render.com (бесплатный тариф)

1. Зарегистрируйтесь на [render.com](https://render.com).
2. **New → Web Service**. Подключите GitHub/ GitLab (или загрузите архив с проектом).
3. Укажите:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Environment** → добавьте переменную **OPENAI_API_KEY** (значение — ваш ключ OpenAI, отмечьте как Secret).
4. Нажмите **Create Web Service**. После сборки сервис получит URL вида `https://fansy-chat.onrender.com`.
5. В файле **embed-fancy-group-ready.txt** замените `https://bot.fancy-group.ru` на этот URL и вставьте код на fancy-group.ru.

Минус бесплатного тарифа: сервис «засыпает» после простоя, первый запрос может быть медленным.

---

## Вариант 2. Railway

1. Зайдите на [railway.app](https://railway.app), подключите репозиторий.
2. **New Project** → **Deploy from GitHub** (выберите репо с этим проектом).
3. В настройках сервиса добавьте переменную **OPENAI_API_KEY**.
4. Railway сам подставит **PORT**; если стартовая команда не подхватилась, задайте вручную:  
   **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. В **Settings → Networking** включите **Generate Domain** — получите URL вида `https://ваш-проект.up.railway.app`.
6. Подставьте этот URL в **embed-fancy-group-ready.txt** и вставьте код на сайт.

---

## Вариант 3. Свой VPS (Ubuntu/Debian)

На сервере с установленным Python 3.10+:

```bash
# Клонирование или загрузка проекта
cd /opt
git clone <ваш-репо> fansy-bot
# или загрузите архив и распакуйте в /opt/fansy-bot
cd fansy-bot

# Виртуальное окружение и зависимости
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ключ (один раз)
export OPENAI_API_KEY="sk-proj-..."
# Или создайте api_key.txt в папке проекта (не коммитьте в git)

# Запуск (для проверки)
uvicorn server:app --host 0.0.0.0 --port 8000
```

Постоянный запуск через systemd:

```bash
sudo nano /etc/systemd/system/fansy.service
```

Содержимое (подставьте свой путь и ключ):

```ini
[Unit]
Description=Fansy Chat Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/fansy-bot
Environment="OPENAI_API_KEY=sk-proj-ВАШ_КЛЮЧ"
ExecStart=/opt/fansy-bot/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Далее:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fansy
sudo systemctl start fansy
```

Настройте Nginx как обратный прокси с HTTPS на порт 8000 и привяжите домен (например, `bot.fancy-group.ru`). URL вида `https://bot.fancy-group.ru` подставьте в **embed-fancy-group-ready.txt**.

---

## Вариант 4. Docker

Сборка и запуск на любой машине с Docker:

```bash
# Сборка (в папке проекта, где лежит Dockerfile)
docker build -t fansy-bot .

# Запуск (ключ — через переменную окружения)
docker run -d -p 8000:8000 -e OPENAI_API_KEY="sk-proj-..." --name fansy fansy-bot
```

Сервис будет доступен на порту 8000. Для продакшена настройте перед контейнером Nginx с HTTPS и подставьте итоговый URL в виджет на fancy-group.ru.

---

После деплоя откройте в браузере:
- `https://ваш-url/health` — должен вернуться `{"status":"ok"}`;
- `https://ваш-url/static/widget.html` — демо-чат.

Затем в **embed-fancy-group-ready.txt** замените `https://bot.fancy-group.ru` на ваш URL и вставьте блок кода в админку сайта fancy-group.ru.
