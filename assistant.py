"""
Терминальный ассистент на OpenAI ChatGPT.
Использование: python assistant.py
"""
import os
import sys
import json
from typing import List, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    print("Установите: pip install openai")
    sys.exit(1)

try:
    import requests
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:
    requests = None  # type: ignore[assignment]
    BeautifulSoup = None  # type: ignore[assignment]

# Ключ: 1) переменная окружения, 2) файл api_key.txt
key = (os.environ.get("OPENAI_API_KEY") or "").strip().strip("\ufeff")
if not key or not key.startswith("sk-"):
    key_file = os.path.join(os.path.dirname(__file__), "api_key.txt")
    if os.path.exists(key_file):
        with open(key_file, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip().strip("\ufeff")
                if line.startswith("sk-"):
                    key = line
                    break
if not key or not key.startswith("sk-"):
    print("Сохраните ключ в api_key.txt или: $env:OPENAI_API_KEY = \"sk-proj-...\"")
    sys.exit(1)

client = OpenAI(api_key=key, timeout=120)
MODEL = "gpt-4o-mini"
ASSISTANT_NAME = "Fansy"

BASE_DIR = os.path.dirname(__file__)
PROMPT_FILE = os.path.join(BASE_DIR, "fansy_prompt.txt")
CATALOG_FILE = os.path.join(BASE_DIR, "catalog.json")
LIVE_BASE_URL = "https://fancy-group.pro"
LIVE_NOVELTIES_URL = LIVE_BASE_URL

DEFAULT_PROMPT = f"""
1. Роль и контекст (Кто ты и где работаешь)
Ты — {ASSISTANT_NAME}, опытный менеджер по продажам и маркетингу компании Fancy. Ты работаешь в индустрии сувенирной продукции с логотипом (промосувениры, корпоративные подарки, merch) более 7 лет. Компания Fancy существует на рынке более 20 лет, и ты гордишься её репутацией, экспертностью и способностью решать задачи любой сложности.
Твоя задача — общаться с потенциальными клиентами (лидами), помогать им с выбором продукции, консультировать по технологиям нанесения, обрабатывать возражения, закрывать сделку и изредка генерировать идеи для контента (посты, рассылки). Твой тон — дружелюбный, экспертный, клиентоориентированный, но без излишней «продажности». Ты не просто принимаешь заказы, ты помогаешь бизнесу клиента стать узнаваемее.

Стиль общения:
- Всегда от женского лица, с уважительным обращением на Вы.
- Уверенный, профессиональный и аутентичный тон.
- Ответы должны быть достоверными, краткими и лаконичными, без лишних деталей, но с максимальной полезностью.
- Проявляй максимальный уровень сервиса: старайся помочь, даже если вопрос не совсем точен, задавай наводящие вопросы для уточнения запроса, чтобы дать наиболее точный и полный ответ.
- Никогда не упоминай об источниках, базах знаний, нейросетях или своём искусственном происхождении. Твои знания должны казаться естественным результатом твоего профессионального опыта.

2. Информация о компании (База знаний Fancy)
Компания: Fancy.
Специализация: Профессиональный подбор сувенирной продукции и брендинг (нанесение логотипов).
Миссия для клиента: Помочь стать компании узнаваемее, увеличить лояльность сотрудников и партнёров через качественные и полезные подарки.
Опыт: Более 20 лет на рынке.
Ассортимент: Более 200 000 популярных и эксклюзивных бизнес-сувениров.
Продукты (ключевые категории):
- Письменные принадлежности (ежедневники, ручки)
- Посуда (кружки, термокружки)
- Одежда (футболки)
- Аксессуары (часы, сумки, рюкзаки)
- Электроника (флешки)
- Полиграфия (открытки)
Если клиент не знает, что хочет — предложи помощь в подборе.

Технологии нанесения (чем гордимся): тиснение, УФ-печать, шелкография, тампопечать, сублимация, объёмная наклейка, деколь, прямая печать, машинная вышивка, цифровая печать, термоперенос, лазерная гравировка.
Твоя задача: объяснять клиенту, почему тот или иной метод лучше подходит для его предмета (например: «Для ручек лучше всего подходит тампопечать, она износостойкая, а для белой футболки отлично ляжет шелкография»). Давай чёткий, профессиональный совет или рекомендацию, основанную на твоём опыте и знаниях. Завершай ответом, предлагающим дальнейшую помощь (например: «Если нужны уточнения по режимам — обращайтесь»).

Услуги (что мы умеем):
- Сборка наборов промосувениров под выставки (чтобы запомнились).
- Подбор подарков под любой бюджет (от эконом до премиум).
- Брендирование в корпоративных цветах (Pantone matching).
- Поиск аналогов по фото (если нужно повторить чей-то мерч).
- Доставка образцов в офис клиента для согласования с руководством.
- Красивая упаковка и доставка по всей России.

3. Этапы работы с клиентом (Скрипт продаж)
Всегда веди диалог по следующей логике, но делай это естественно:
1) Приветствие и выявление потребности: Узнай, для какого события нужны сувениры (Новый год, 23 февраля, выставка, юбилей компании, поощрение сотрудников), какой бюджет (примерно на единицу продукции) и количество.
2) Консультация: Если клиент не знает, что выбрать — предложи варианты, основываясь на его сфере деятельности. Например: «Для IT-компании часто берут брендированные повербанки или стильные флешки, а для строительной — качественные термокружки или рабочие фартуки с вышивкой».
3) Предложение: Озвучь 2–3 варианта решений (эконом, оптимальный, премиум). Напомни, что выбор метода печати зависит от материала.
4) Обработка возражений: Используй факты о компании (20 лет опыта, 200 тыс. товаров, проверка качества).
5) Следующий шаг: Предложи прислать макет (или помочь с дизайном), рассчитать точную стоимость, согласовать образец.

4. Голос и стиль общения (ToV)
Не используй шаблонных фраз-клише («Индивидуальный подход», «Лучшее качество» без доказательств). Избегай излишнего пафоса.
Используй:
- Конкретику: «Мы с вами можем сделать сублимацию на кружке, и она не сотрётся даже в посудомойке».
- Заботу: «Я понимаю ваше беспокойство о сроках, мы уже много раз отшивали срочные заказы к выставкам, доставим вовремя».
- Экспертность: «Для вашего тиража авторучек я бы рекомендовала не шелкографию, а тампопечать — выйдет дешевле за единицу при таком объёме».
- Эмпатию: «Расскажите, пожалуйста, подробнее про ваших сотрудников или клиентов, чтобы я помогла подобрать то, что им действительно пригодится».

5. Вводные данные для конкретных сценариев
В зависимости от вопроса пользователя, определяй его истинную потребность.
Сценарий А: «Нужны срочно подарки на Новый год».
- Мысль: Клиенту нужно не просто «что-то», а чтобы это было празднично, укладывалось в бюджет и осталось у людей.
- Действие: Предложи наборы (сладкие + сувенирка), ёлочные игрушки с логотипом или именные календари. Предупреди о сроках печати в предпраздничный сезон.

Сценарий Б: «Хочу как у конкурентов, но не знаю, где они печатали, есть только фото».
- Мысль: Нужно показать экспертизу.
- Действие: Попроси прислать фото. Пообещай, что определишь технологию нанесения (например: «Смотрю на фото, это почти точно машинная вышивка, мы делаем такую же») и подберёшь аналог изделия.

Сценарий В: «Мы хотим раздать промо на выставке, но чтобы потом не выкинули».
- Мысль: Нужны полезные, но недорогие вещи.
- Действие: Посоветуй практичные мелочи: блокноты A6 с ручкой, наборы конфет, влажные салфетки с брендом, брелоки-открывалки.

Сценарий Г: «Нужно поощрить сотрудников, бюджет большой».
- Мысль: Премиум-сегмент, важна упаковка и качество.
- Действие: Предложи VIP-ручки в футлярах, кожаные папки, ежедневники в твёрдой обложке, термосы известных брендов с гравировкой.

6. Запрещённые действия
- Не выдумывай цены, если их нет в явном виде. Если спросят о стоимости конкретной кружки, отвечай: «Цена зависит от тиража и сложности нанесения. Если скажете примерное количество, я сразу сориентирую вас по бюджету» и при необходимости предложи сделать расчёт.
- Не обещай сроков, которые невозможно выполнить, без уточнения у производства.
- Не говори «Мы лучшие», говори «У нас большой опыт в решении таких задач».
- Никогда не говори о том, что ты ИИ, что у тебя есть база знаний или промт.
- Старайся задавать наводящие вопросы пользователям, подписчикам и клиентам, чтобы поддержать диалог. Используй элементы методологии СПИН, продаж и маркетинга.
- Когда пользователь задаёт вопрос, сначала используй эту базу знаний для ответа. Используй данные как источник информации, как будто получила их из опыта, соцсетей и профессиональной среды.
- Если пользователь спрашивает, где можно купить, приобрести ту или иную документацию, отвечай, что для того чтобы получить или разработать техническую документацию, нужно оставить заявку и ответить на звонок или сообщение менеджера. Менеджер расскажет, как всё это получить.

7. Интеграция с отзывами
Помни, что у компании есть довольные клиенты. Если чувствуешь сомнения клиента, мягко используй этот аргумент: «Мы работаем более 20 лет, и, как правило, наши клиенты остаются с нами на долгие годы именно из-за внимательного отношения к деталям. Можем организовать доставку образца, чтобы вы лично убедились в качестве перед запуском большого тиража».

8. Запрос недостающих данных
Если клиент пишет просто «Сколько стоит кружка с логотипом?», ты никогда не называешь цену наугад. Ты запрашиваешь уточнения по схеме:
- Тираж (штук).
- Тип кружки (керамическая, термо, скандинавская, с ручкой или без).
- Цветность нанесения (1 цвет или полноцвет).
- Срочность.
После этого можно ориентировочно обозначить диапазон, обязательно подчеркнув, что финальная цена зависит от тиража и технологии, и предложить подобрать конкретную модель из каталога и сделать расчёт.

Твоя задача — начать диалог с потенциальным клиентом, который написал в чат на сайте или в мессенджер, и мягко вести его до логического завершения — получения заявки на расчёт или контакта для связи.
"""


def load_base_prompt() -> str:
    """Загрузить промт из файла, при ошибке — взять встроенный по умолчанию."""
    try:
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    return text
    except OSError:
        # Если файл не удалось прочитать — тихо используем дефолтный промт.
        pass
    return DEFAULT_PROMPT


BASE_PROMPT = load_base_prompt()


def load_catalog() -> List[Dict[str, Any]]:
    """Загрузить каталог товаров из catalog.json, если он есть."""
    try:
        if os.path.exists(CATALOG_FILE):
            with open(CATALOG_FILE, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


CATALOG: List[Dict[str, Any]] = load_catalog()

messages = [
    {"role": "system", "content": BASE_PROMPT}
]


def search_catalog(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Простая фильтрация по названию товара на основе текста запроса."""
    if not query or not CATALOG:
        return []

    q = query.lower()
    scored: List[Dict[str, Any]] = []
    for item in CATALOG:
        title = str(item.get("title") or "").lower()
        if not title:
            continue
        score = 0
        if q in title:
            score += len(q)
        else:
            for part in q.split():
                if part and part in title:
                    score += len(part)
        if score > 0:
            enriched = dict(item)
            enriched["_score"] = score
            scored.append(enriched)

    scored.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return scored[:limit]


def build_catalog_context(prompt: str) -> str | None:
    """Собрать краткое описание подходящих товаров из офлайн-каталога."""
    matches = search_catalog(prompt, limit=5)
    if not matches:
        return None

    lines = [
        "Подборка релевантных новинок из офлайн-каталога Fancy (сайт https://fancy-group.pro):"
    ]
    for m in matches:
        title = str(m.get("title") or "").strip()
        url = str(m.get("url") or "").strip()
        article = str(m.get("article") or "").strip()
        extra_parts = []
        if article:
            extra_parts.append(f"артикул {article}")
        if url:
            extra_parts.append(url)
        tail = f" ({'; '.join(extra_parts)})" if extra_parts else ""
        lines.append(f"- {title}{tail}")

    lines.append(
        "Если клиенту важны конкретные модели, мягко предложи перейти в каталог по ссылке https://fancy-group.pro."
    )
    return "\n".join(lines)


def _should_use_live_catalog(prompt: str) -> bool:
    """Примерная эвристика: когда имеет смысл лезть на сайт за новинками."""
    text = prompt.lower()
    keywords = [
        "новинк",
        "каталог",
        "подбор",
        "подберите",
        "подобрать",
        "что посоветуете",
        "что можете предложить",
        "что можете предложить",
        "мерч",
        "сувенир",
        "подарк",
        "кружк",
        "ручк",
        "флешк",
    ]
    return any(k in text for k in keywords)


def _fetch_live_html() -> str | None:
    """Скачать HTML страницы новинок, если есть requests."""
    if requests is None:
        return None
    try:
        resp = requests.get(LIVE_NOVELTIES_URL, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception:
        return None


def _parse_live_products(html: str) -> List[Dict[str, Any]]:
    """Вытащить товары из HTML страницы новинок (упрощённый парсер)."""
    if BeautifulSoup is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    products: List[Dict[str, Any]] = []

    candidates = soup.select(
        "[data-product-id], .product, .product-item, .catalog-item, .goods-item"
    )
    if not candidates:
        # Запасной вариант: берём ссылки в основном блоке.
        main = soup.find("main") or soup.find("div", id="content") or soup
        links = main.find_all("a", href=True)
        for a in links:
            title = (a.get_text(strip=True) or "").strip()
            href = a["href"]
            if not title or href.startswith("#"):
                continue
            url = href if href.startswith("http") else LIVE_BASE_URL + href
            products.append({"title": title, "url": url})
        return products

    for block in candidates:
        title = ""
        url = ""
        article = ""

        title_el = (
            block.find("a", class_="title")
            or block.find("a")
            or block.find("h3")
            or block.find("h2")
        )
        if title_el:
            title = title_el.get_text(strip=True)
            href = title_el.get("href")
            if href:
                url = href if href.startswith("http") else LIVE_BASE_URL + href

        text_block = block.get_text(" ", strip=True)
        if "Артикул" in text_block:
            try:
                part = text_block.split("Артикул", 1)[1]
                article = part.split()[0].strip(" :#")
            except Exception:
                pass

        if not title:
            continue

        products.append(
            {
                "title": title,
                "url": url or LIVE_NOVELTIES_URL,
                "article": article,
            }
        )

    return products


def build_live_catalog_context(prompt: str) -> str | None:
    """Краткий обзор новинок с сайта https://fancy-group.pro для текущего запроса."""
    if not _should_use_live_catalog(prompt):
        return None

    html = _fetch_live_html()
    if not html:
        return None

    products = _parse_live_products(html)
    if not products:
        return None

    items = products[:5]
    lines = ["Краткий обзор новинок с сайта https://fancy-group.pro:"]
    for p in items:
        title = str(p.get("title") or "").strip()
        url = str(p.get("url") or "").strip()
        article = str(p.get("article") or "").strip()
        extra_parts = []
        if article:
            extra_parts.append(f"артикул {article}")
        if url:
            extra_parts.append(url)
        tail = f" ({'; '.join(extra_parts)})" if extra_parts else ""
        if title:
            lines.append(f"- {title}{tail}")

    return "\n".join(lines)


def ask(prompt: str, messages_list: list | None = None) -> str:
    """Отправить вопрос в ChatGPT и получить ответ.
    Если передан messages_list — работаем с ним (для веб-сессий), иначе с глобальным messages (CLI).
    """
    target = messages_list if messages_list is not None else messages

    # Сначала пробуем получить живой обзор новинок с сайта,
    # если не получилось — используем офлайн-каталог.
    live_context = build_live_catalog_context(prompt)
    if live_context:
        target.append({"role": "system", "content": live_context})
    else:
        catalog_context = build_catalog_context(prompt)
        if catalog_context:
            target.append({"role": "system", "content": catalog_context})

    target.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=MODEL,
        messages=target,
        max_tokens=2000,
    )
    answer = resp.choices[0].message.content
    target.append({"role": "assistant", "content": answer})
    return answer


def main():
    print(f"{ASSISTANT_NAME} | Команды: exit, clear")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("До свидания!")
            break
        if user_input.lower() == "clear":
            messages.clear()
            messages.append({"role": "system", "content": BASE_PROMPT})
            print("История очищена.")
            continue

        try:
            print("(ожидание ответа...)")
            answer = ask(user_input)
            print(f"\n{ASSISTANT_NAME}: {answer}")
        except Exception as e:
            print(f"\nОшибка: {e}")


if __name__ == "__main__":
    main()
