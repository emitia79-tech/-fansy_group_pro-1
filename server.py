"""
Веб-сервер для чат-бота Fansy (FastAPI).
Раздаёт API /chat и статику виджета (fansy-widget.js, widget.html).
Запуск: uvicorn server:app --host 0.0.0.0 --port 8000
Для сайта fancy-group.pro: разрешён CORS с этого origin.
"""
import os
import uuid
from typing import Optional

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
except ImportError:
    print("Установите: pip install fastapi uvicorn pydantic")
    raise

# Импорт после проверки ключа в assistant
from assistant import BASE_DIR, ask, BASE_PROMPT

app = FastAPI(title="Fansy Chat API", version="1.0")

# Раздача виджета из папки static/ (без доступа к api_key и др.)
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# CORS: разрешаем запросы с сайта fancy-group.pro и с локального хоста для тестов
ALLOWED_ORIGINS = [
    "https://fancy-group.pro",
    "http://fancy-group.pro",
    "http://localhost",
    "http://127.0.0.1",
]
for port in ("8000", "3000", "5500"):
    ALLOWED_ORIGINS.append(f"http://localhost:{port}")
    ALLOWED_ORIGINS.append(f"http://127.0.0.1:{port}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Сессии: session_id -> список сообщений (как в assistant)
sessions: dict[str, list] = {}


def get_session(session_id: str) -> list:
    """Вернуть список сообщений для сессии, создав его при первом обращении."""
    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": BASE_PROMPT}]
    return sessions[session_id]


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Принять сообщение пользователя и вернуть ответ бота."""
    text = (request.message or "").strip()
    if not text:
        return ChatResponse(reply="Напишите, пожалуйста, ваш вопрос.", session_id=request.session_id or "")

    session_id = request.session_id or str(uuid.uuid4())
    messages_list = get_session(session_id)

    try:
        reply = ask(text, messages_list=messages_list)
    except Exception as e:
        reply = f"Произошла ошибка при обработке запроса. Попробуйте позже или свяжитесь с нами: +7 495 108-07-95."
        # В продакшене лучше логировать e, не отдавать клиенту

    return ChatResponse(reply=reply, session_id=session_id)


@app.get("/health")
def health():
    """Проверка доступности сервера."""
    return {"status": "ok"}
