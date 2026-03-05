# Виджет чата Fansy для сайта fancy-group.ru

## 1. Запуск API-сервера

Установите зависимости (если ещё не установлены):

```bash
pip install fastapi uvicorn pydantic
```

В папке проекта запустите:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу `http://localhost:8000`. Эндпоинты:

- `POST /chat` — отправка сообщения боту (тело: `{"message": "текст", "session_id": "..."}`).
- `GET /health` — проверка работы сервера.

## 2. Вставка виджета на сайт

### Вариант A: виджет на том же домене, что и API

Если фронт сайта fancy-group.ru и бэкенд раздаются с одного домена (или через прокси), подключите скрипт и инициализируйте виджет с путём к API:

```html
<script src="https://ваш-домен/путь/fansy-widget.js"></script>
<script>
  FansyWidget.init({
    apiUrl: 'https://ваш-домен/api/chat',  // URL до POST /chat
    title: 'Fansy',
    subtitle: 'Помогу с подбором сувениров',
    placeholder: 'Напишите сообщение...',
    sendLabel: 'Отправить',
    openLabel: 'Чат',
  });
</script>
```

### Вариант B: API на отдельном сервере

Если бот крутится на отдельном домене (например, `https://bot.fancy-group.ru`), укажите полный URL:

```html
<script src="https://fancy-group.ru/static/fansy-widget.js"></script>
<script>
  FansyWidget.init({
    apiUrl: 'https://bot.fancy-group.ru/chat',
    title: 'Fansy',
    subtitle: 'Помогу с подбором сувениров',
  });
</script>
```

В `server.py` в списке `ALLOWED_ORIGINS` уже указаны `https://fancy-group.ru` и `http://fancy-group.ru`, так что CORS для запросов с сайта разрешён.

### Параметры `FansyWidget.init()`

| Параметр      | По умолчанию                    | Описание                          |
|---------------|---------------------------------|-----------------------------------|
| `apiUrl`      | `'/chat'`                       | URL эндпоинта (POST), без слэша в конце |
| `title`       | `'Fansy'`                       | Заголовок панели чата             |
| `subtitle`    | `'Помогу с подбором сувениров'` | Подзаголовок                      |
| `placeholder` | `'Напишите сообщение...'`       | Плейсхолдер поля ввода            |
| `sendLabel`   | `'Отправить'`                   | Текст кнопки отправки             |
| `openLabel`   | `'Чат'`                         | Текст кнопки открытия чата         |
| `errorMessage`| Сообщение об ошибке             | Текст при сбое запроса            |

## 3. Локальная проверка

1. Запустите сервер: `uvicorn server:app --reload --port 8000`.
2. Откройте в браузере `widget.html` (через любой простой HTTP-сервер, например `python -m http.server 5500` в папке проекта, затем `http://127.0.0.1:5500/widget.html`), либо отдайте `widget.html` и `fansy-widget.js` через тот же uvicorn (для этого нужно добавить раздачу статики в FastAPI — см. документацию FastAPI StaticFiles).
3. В `widget.html` в `apiUrl` указан `http://127.0.0.1:8000/chat` — при необходимости измените на свой адрес.

## 4. Деплой сервера в прод

- Разместите проект на VPS/хостинге (Python 3.10+).
- Задайте переменную окружения `OPENAI_API_KEY` или положите ключ в `api_key.txt`.
- Запустите через systemd/supervisor или аналог: `uvicorn server:app --host 0.0.0.0 --port 8000`.
- Настройте Nginx (или аналог) как обратный прокси до `http://127.0.0.1:8000`, при необходимости включите HTTPS.
- Убедитесь, что в `ALLOWED_ORIGINS` в `server.py` указан фактический origin сайта (например, `https://fancy-group.ru`).

После этого виджет на сайте будет отправлять запросы на ваш сервер и показывать ответы бота Fansy.
