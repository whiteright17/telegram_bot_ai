import telebot
import openai
from config import TelegramKey, OpenAiKey

openai.api_key = OpenAiKey
bot = telebot.TeleBot(TelegramKey)

# Словарь для отслеживания состояния пользователя (ожидание prompt для изображения)
user_state = {}


@bot.message_handler(commands=['start'])
def welcome(message):
    print("Команда /start получена")  # Логирование получения команды
    bot.send_message(message.chat.id, 'Привіт. Напиши мову спілкування')


@bot.message_handler(commands=['generate'])
def ask_for_prompt(message):
    user_state[message.chat.id] = 'AWAITING_PROMPT'  # Устанавливаем состояние ожидания prompt
    bot.send_message(message.chat.id, 'Опишіть бажану картинку. \nПриклад: Фон для обкладинки в Youtube в стилі модерн')




@bot.message_handler(content_types=['text'])
def handle_text(message):
    if user_state.get(message.chat.id) == 'AWAITING_PROMPT':
        # Пользователь ввел prompt, генерируем изображение
        prompt_text = message.text
        user_state[message.chat.id] = None  # Сброс состояния
        generate_image(message, prompt_text)
    else:
        # Обработка обычного текстового сообщения
        handle_conversation(message)


def handle_conversation(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Вы в чате с AI."},
                  {"role": "user", "content": message.text}]
    )
    gpt_text = response['choices'][0]['message']['content']
    bot.send_message(message.chat.id, gpt_text)


def generate_image(message, prompt_text):
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response['data'][0]['url']
        bot.send_photo(message.chat.id, image_url)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при генерации изображения.")


bot.polling(non_stop=True)
