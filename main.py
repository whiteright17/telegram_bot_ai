import telebot
import openai
from config import TelegramKey, OpenAiKey

openai.api_key = OpenAiKey
bot = telebot.TeleBot(TelegramKey)

# User State Tracking Dictionary (Waiting for Image Prompt)
user_state = {}


@bot.message_handler(commands=['start'])
def welcome(message):
    print("Команда /start получена")  # Logging the Receipt of a Command
    bot.send_message(message.chat.id, 'Hello. Your text.....')


@bot.message_handler(commands=['generate'])
def ask_for_prompt(message):
    user_state[message.chat.id] = 'AWAITING_PROMPT'  # Setting the Waiting for Prompt State
    bot.send_message(message.chat.id, 'Setting the Waiting for Prompt State')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if user_state.get(message.chat.id) == 'AWAITING_PROMPT':
        # The user entered a prompt, we generate an image.
        prompt_text = message.text
        user_state[message.chat.id] = None  # State Reset
        generate_image(message, prompt_text)
    else:
        # Processing a Regular Text Message
        handle_conversation(message)


def handle_conversation(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are in a chat with AI."},
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
        print(f"An error occurred: {e}")
        bot.send_message(message.chat.id, "An error occurred during image generation.")


bot.polling(non_stop=True)
