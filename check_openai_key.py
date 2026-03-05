"""Проверка работы OpenAI API ключа."""
import os
import sys

def safe_print(*args):
    text = " ".join(str(a) for a in args)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode())

try:
    from openai import OpenAI
except ImportError:
    safe_print("Install: pip install openai")
    sys.exit(1)

key = os.environ.get("OPENAI_API_KEY")
if not key or key in ("your_key", "ваш_ключ", "сюда_вставьте_ваш_новый_ключ"):
    safe_print("Set key: $env:OPENAI_API_KEY = \"sk-proj-...\" (your real key)")
    sys.exit(1)

client = OpenAI(api_key=key)
try:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=10,
    )
    msg = resp.choices[0].message.content
    safe_print("Key OK. Response:", msg)
except Exception as e:
    err_msg = str(e).encode("ascii", "replace").decode()
    safe_print("Error:", err_msg)
    sys.exit(1)
