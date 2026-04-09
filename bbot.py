import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import os
import random
import json

# ==================================================
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (настройки на хостинге)
# ==================================================
ACCESS_TOKEN = os.environ.get("VK_TOKEN")
GROUP_ID = int(os.environ.get("GROUP_ID", 0))

if not ACCESS_TOKEN:
    print("❌ Ошибка: не задана переменная VK_TOKEN")
    exit(1)
if not GROUP_ID:
    print("❌ Ошибка: не задана переменная GROUP_ID")
    exit(1)

# ==================================================
# БАЗА ДАННЫХ БОТА
# ==================================================

FAKE_NEWS_DB = [
    {
        "text": "СРОЧНО! В школах Москвы с 1 сентября отменяют домашние задания!",
        "is_fake": True,
        "explanation": "❌ Это ФЕЙК! Официальных заявлений об отмене домашних заданий не поступало. Признаки: эмоциональный заголовок, отсутствие ссылки на источник."
    },
    {
        "text": "ВКонтакте запускает новый формат коротких видео — «Клипы». Информация опубликована в официальном блоге VK.",
        "is_fake": False,
        "explanation": "✅ Это ПРАВДА. Информация подтверждена официальным источником."
    },
    {
        "text": "Внимание! Новый вирус в WhatsApp! Не открывайте сообщение с темой «Привет, это видео про тебя» — оно взламывает телефон!",
        "is_fake": True,
        "explanation": "❌ Это ФЕЙК! Такие сообщения — классический вирусный фейк. WhatsApp не может взломать телефон просто от открытия сообщения."
    },
    {
        "text": "С 1 января 2025 года в России введут налог на отправку сообщений в мессенджерах.",
        "is_fake": True,
        "explanation": "❌ Это ФЕЙК! Информация не подтверждена официальными источниками."
    },
    {
        "text": "Google запустил новый искусственный интеллект, который пишет музыку.",
        "is_fake": False,
        "explanation": "✅ Это ПРАВДА. Google действительно разрабатывает музыкальные нейросети."
    }
]

LAW_CASES_DB = [
    {
        "text": "Ты опубликовал в соцсети фото одноклассника без его согласия. Он требует удалить. Кто прав?",
        "correct": "Одноклассник",
        "explanation": "⚖️ Статья 152.1 ГК РФ: публикация фото без согласия нарушает закон."
    },
    {
        "text": "Тебе пришло сообщение: «Ваш аккаунт ВК будет заблокирован, перейдите по ссылке и подтвердите пароль». Что делать?",
        "correct": "Не переходить по ссылке",
        "explanation": "🔒 Это ФИШИНГ. Настоящая техподдержка никогда не просит пароль."
    },
    {
        "text": "Ты написал в комментариях оскорбление. Какая ответственность грозит?",
        "correct": "Штраф до 10 000 рублей",
        "explanation": "⚖️ Статья 5.61 КоАП РФ «Оскорбление»: штраф от 3000 до 10 000 рублей."
    },
    {
        "text": "Ты сделал репост новости, которая оказалась фейком. Тебе грозит ответственность?",
        "correct": "Да, даже за репост",
        "explanation": "⚖️ Статья 207.3 УК РФ: распространение фейков наказывается штрафом до 1,5 млн рублей."
    }
]

RULES_TEXT = """
📋 *20 правил цифровой безопасности*

🔧 *Технические правила:*
1️⃣ Сложные пароли (12+ символов)
2️⃣ Двухфакторная аутентификация
3️⃣ Проверяй адрес сайта перед вводом пароля
4️⃣ Регулярно обновляй программы
5️⃣ Не скачивай файлы с непроверенных сайтов

🧠 *Поведенческие правила:*
6️⃣ Проверяй новости в 3 источниках
7️⃣ Не публикуй личные данные в открытом доступе
8️⃣ Не общайся с навязчивыми незнакомцами
9️⃣ Делай скриншоты при кибербуллинге
🔟 Не распространяй непроверенную информацию

⚖️ *Правовые правила:*
1️⃣1️⃣ Не публикуй чужие фото без согласия (ст. 152.1 ГК РФ)
1️⃣2️⃣ Не распространяй личную информацию (ст. 137 УК РФ)
1️⃣3️⃣ Не оскорбляй людей в сети (ст. 5.61 КоАП РФ)
1️⃣4️⃣ Не распространяй фейки (ст. 207.3 УК РФ)
1️⃣5️⃣ Соблюдай авторские права
"""

TEST_QUESTIONS = [
    {
        "text": "Что такое фишинг?",
        "options": ["Вид рыбной ловли", "Интернет-мошенничество для кражи паролей", "Антивирус", "Правило гигиены"],
        "correct": 1
    },
    {
        "text": "Можно ли опубликовать фото друга без его согласия?",
        "options": ["Да", "Нет, это нарушает ст. 152.1 ГК РФ", "Можно, если фото красивое", "Можно, если друг не узнает"],
        "correct": 1
    },
    {
        "text": "Какой пароль самый надёжный?",
        "options": ["123456", "qwerty", "МойКотВася2024!", "password"],
        "correct": 2
    },
    {
        "text": "Что делать при получении подозрительной ссылки от «техподдержки»?",
        "options": ["Перейти и ввести пароль", "Проигнорировать", "Переслать друзьям", "Написать комментарий"],
        "correct": 1
    },
    {
        "text": "Какая статья защищает право на изображение?",
        "options": ["Статья 137 УК РФ", "Статья 152.1 ГК РФ", "Статья 207.3 УК РФ", "Статья 5.61 КоАП РФ"],
        "correct": 1
    }
]

# ==================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==================================================

user_states = {}

def send_message(user_id, message, keyboard=None):
    params = {
        "user_id": user_id,
        "message": message,
        "random_id": random.randint(1, 2**32)
    }
    if keyboard:
        params["keyboard"] = keyboard
    
    vk.messages.send(**params)
def create_main_keyboard():
    keyboard = {
        "one_time": False,
        "buttons": [
            [
                {"action": {"type": "text", "label": "🛡️ Проверь новость"}, "color": "primary"},
                {"action": {"type": "text", "label": "⚖️ Юридический кейс"}, "color": "primary"}
            ],
            [
                {"action": {"type": "text", "label": "📚 Правила"}, "color": "secondary"},
                {"action": {"type": "text", "label": "📝 Тест"}, "color": "secondary"}
            ],
            [
                {"action": {"type": "text", "label": "❓ Помощь"}, "color": "secondary"}
            ]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)

def create_yes_no_keyboard():
    keyboard = {
        "one_time": True,
        "buttons": [
            [
                {"action": {"type": "text", "label": "✅ Правда"}, "color": "primary"},
                {"action": {"type": "text", "label": "❌ Фейк"}, "color": "negative"}
            ]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)

def create_quiz_keyboard(options):
    buttons = []
    row = []
    for i, opt in enumerate(options):
        row.append({"action": {"type": "text", "label": opt}, "color": "primary"})
        if len(row) == 2 or i == len(options) - 1:
            buttons.append(row)
            row = []
    keyboard = {"one_time": True, "buttons": buttons}
    return json.dumps(keyboard, ensure_ascii=False)

# ==================================================
# ОБРАБОТЧИКИ КОМАНД
# ==================================================

def handle_fake_check(user_id):
    news = random.choice(FAKE_NEWS_DB)
    user_states[user_id] = {"module": "fake_check", "news": news}
    send_message(user_id, f"📰 *Проверь новость*\n\n{news['text']}\n\nПравда или фейк?", create_yes_no_keyboard())

def handle_fake_answer(user_id, answer):
    state = user_states.get(user_id, {})
    news = state.get("news", {})
    user_is_fake = "фейк" in answer.lower() or "❌" in answer
    is_correct = (user_is_fake == news.get("is_fake"))
    
    if is_correct:
        response = f"✅ *Правильно!*\n\n{news.get('explanation', '')}"
    else:
        response = f"❌ *Неправильно!*\n\n{news.get('explanation', '')}"
    
    send_message(user_id, response, create_main_keyboard())
    user_states.pop(user_id, None)

def handle_law_case(user_id):
    case = random.choice(LAW_CASES_DB)
    send_message(user_id, f"⚖️ *Юридический кейс*\n\n{case['text']}\n\n{case['correct']}\n\n{case['explanation']}", create_main_keyboard())

def handle_rules(user_id):
    send_message(user_id, RULES_TEXT, create_main_keyboard())

def handle_help(user_id):
    help_text = """❓ *Команды бота*

• 🛡️ Проверь новость — распознай фейк
• ⚖️ Юридический кейс — правовая ситуация
• 📚 Правила — 20 правил безопасности
• 📝 Тест — проверь знания

Бот по медиаграмотности и правовой культуре."""
    send_message(user_id, help_text, create_main_keyboard())

def handle_test(user_id):
    user_states[user_id] = {
        "module": "test",
        "questions": TEST_QUESTIONS.copy(),
        "current_q": 0,
        "score": 0
    }
    send_test_question(user_id)

def send_test_question(user_id):
    state = user_states.get(user_id, {})
    questions = state.get("questions", [])
    current = state.get("current_q", 0)
    
    if current < len(questions):
        q = questions[current]
        text = f"📝 *Вопрос {current + 1} из {len(questions)}*\n\n{q['text']}"
        send_message(user_id, text, create_quiz_keyboard(q['options']))
    else:
        score = state.get("score", 0)
        total = len(questions)
        percent = (score / total) * 100
        result = f"🎉 *Тест завершён!*\n\nРезультат: {score} из {total} ({percent:.0f}%)"
        send_message(user_id, result, create_main_keyboard())
        user_states.pop(user_id, None)

def handle_test_answer(user_id, answer):
    state = user_states.get(user_id, {})
    questions = state.get("questions", [])
    current = state.get("current_q", 0)
    
    if current < len(questions):
        q = questions[current]
        selected_idx = None
        for i, opt in enumerate(q['options']):
            if opt.lower() == answer.lower():
                selected_idx = i
                break
        
        if selected_idx == q['correct']:
            state["score"] = state.get("score", 0) + 1
            send_message(user_id, "✅ Верно!")
        else:
            send_message(user_id, f"❌ Неверно. Правильный ответ: {q['options'][q['correct']]}")
        
        state["current_q"] = current + 1
        user_states[user_id] = state
        send_test_question(user_id)

# ==================================================
# ОСНОВНОЙ ЦИКЛ
# ==================================================

vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

print("✅ Бот запущен и готов к работе!")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_user:
            user_id = event.message['from_id']
            message_text = event.message['text'].lower().strip()
            
            print(f"📩 Сообщение от {user_id}: {message_text}")
            
            # Обработка команд (без приветствия)
            if message_text in ["помощь", "help", "?", "❓ Помощь"]:
                handle_help(user_id)
            
            elif message_text in ["правила", "rules", "📚 Правила"]:
                handle_rules(user_id)
            
            elif message_text in ["тест", "test", "📝 Тест"]:
                handle_test(user_id)
            
            elif "проверь новость" in message_text or message_text in ["фейк", "новость"]:
                handle_fake_check(user_id)
            
            elif "юридический кейс" in message_text or message_text in ["кейс", "юрист"]:
                handle_law_case(user_id)
            
            elif user_id in user_states and user_states[user_id].get("module") == "test":
                handle_test_answer(user_id, message_text)
            
            elif user_id in user_states and user_states[user_id].get("module") == "fake_check":
                handle_fake_answer(user_id, message_text)
            
            # Если команда не распознана — бот молчит (ничего не отправляет)
