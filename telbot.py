import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import requests
import datetime

bot = Bot(token='6964370519:AAETLP2uaIyHbtpp3JRaoeqKlIAH7mm6bsc')
dp = Dispatcher(bot)

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Set City'))

user_city = {}  # Dictionary to store user-selected cities
default_city = {}  # Dictionary to store default cities

# Dictionary mapping weather types to emojis
weather_emojis = {
     "ясно": "☀️",
    "малооблачно": "⛅️",
    "облачно с прояснениями": "🌤️",
    "переменная облачность": "🌥️",
    "облачно": "☁️",
    "небольшой дождь": "🌧️",
    "дождь": "🌧️",
    "проливной дождь": "⛈️",
    "легкий снег": "🌨️",
    "снег": "❄️",
    "небольшой снег": "🌨️",
    "гроза": "⛈️",
    "туман": "🌫️",
    "пасмурно": "☁️",
    "небольшая облачность": "🌥️"
}

async def send_hourly_weather_notification(city, chat_id):
    try:
        open_weather_token = 'f8c9e0a759bf609bf41e844d4b02dc54'

        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        temp = data['main']['temp']
        description = data['weather'][0]['description']
        weather_type = data['weather'][0]['main']

        emoji = weather_emojis.get(weather_type, '')  # Get emoji for weather type

        if temp < -25:
            result = 'Очень холодно, лучше всего остаться дома.'
        elif temp < 0:
            result = 'Холодно, одевайтесь теплее.'
        elif temp < 10:
            result = 'Прохладно, лучше надеть куртку.'
        elif temp < 20:
            result = 'Тепло, на улице приятно.'
        elif temp < 30:
            result = 'Жарко, можете надеть что-то легкое.'
        else:
            result = 'Очень жарко, наденьте что-то легкое и пейте воду.'

        await bot.send_message(chat_id, f"Сейчас в городе {city} {description} {emoji}, температура {temp}°C. {result}")

    except Exception as ex:
        await bot.send_message(chat_id, f"Ошибка при получении погоды для города {city}: {ex}")

async def hourly_weather_notifications():
    while True:
        await asyncio.sleep(60)  # Задержка
        for chat_id, city in default_city.items():
            await send_hourly_weather_notification(city, chat_id)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет! Я могу отправлять тебе информацию о погоде в твоем городе. '
                                                  'Для начала выбери свой основной город.', reply_markup=start_keyboard)

@dp.message_handler(text='Set City')
async def set_city(message: types.Message):
    await bot.send_message(message.from_user.id, 'Введите свой основной город:')
    user_city[message.from_user.id] = True

@dp.message_handler(content_types=["text"])
async def get_weather_info(message: types.Message):
    try:
        open_weather_token = 'f8c9e0a759bf609bf41e844d4b02dc54'
        weather_emojis = {
            "ясно": "☀️",
            "малооблачно": "⛅️",
            "облачно с прояснениями": "🌤️",
            "переменная облачность": "🌥️",
            "облачно": "☁️",
            "небольшой дождь": "🌧️",
            "дождь": "🌧️",
            "проливной дождь": "⛈️",
            "легкий снег": "🌨️",
            "снег": "❄️",
            "небольшой снег": "🌨️",
            "гроза": "⛈️",
            "туман": "🌫️",
            "пасмурно": "☁️",
            "небольшая облачность": "🌥️"
        }
        
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&lang=ru&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        weather_type = data['weather'][0]['main']
        emoji = weather_emojis.get(description, "")
        
        if temp < -25:
            result = 'Очень холодно, лучше всего остаться дома.'
        elif temp < 0:
            result = 'Холодно, одевайтесь теплее.'
        elif temp < 10:
            result = 'Прохладно, лучше надеть куртку.'
        elif temp < 20:
            result = 'Тепло, на улице приятно.'
        elif temp < 30:
            result = 'Жарко, можете надеть что-то легкое.'
        else:
            result = 'Очень жарко, наденьте что-то легкое и пейте воду.'
            
        # Формируем текст сообщения
        message_text = f"<b>Сейчас в городе {message.text}</b>\n\n"\
                       f"<i>Температура:</i> {temp}°C\n"\
                       f"<i>Погода:</i> {description} {emoji}\n"\
                       f"<i>Рекомендации:</i> {result}\n"
        
        # Отправляем сообщение с изображением и текстом
        with open("./images/жарко.jpg", "rb") as photo_file:
            await bot.send_photo(
                message.chat.id,
                photo=photo_file,
                caption=message_text,
                parse_mode="HTML"
            )

        # Добавляем клавиатуру для выбора прогноза погоды
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Погода на 1 день", callback_data=f"weather_forecast_1_{message.text}"))
        keyboard.add(types.InlineKeyboardButton(text="Погода на 3 дня", callback_data=f"weather_forecast_3_{message.text}"))
        keyboard.add(types.InlineKeyboardButton(text="Погода на 7 дней", callback_data=f"weather_forecast_7_{message.text}"))
        await bot.send_message(message.from_user.id, "Выберите интересующий вас прогноз погоды:", reply_markup=keyboard)
        
        # Сохраняем выбранный пользователем город как его основной
        default_city[message.from_user.id] = message.text

    except Exception as ex:
        await bot.send_message(message.from_user.id, "Проверьте название города")

@dp.callback_query_handler(lambda query: query.data.startswith('weather_forecast_'))
async def send_weather_forecast(callback_query: types.CallbackQuery):
    forecast_days = int(callback_query.data.split('_')[2])
    city = callback_query.data.split('_')[3]

    try:
        open_weather_token = 'f8c9e0a759bf609bf41e844d4b02dc54'

        if forecast_days == 1:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric&lang=ru"
            )
            data = r.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            emoji = weather_emojis.get(description, "")

            await bot.send_message(callback_query.from_user.id, f"{emoji} Сейчас в городе {city}: {description}, температура {temp}°C.")

        elif forecast_days == 3 or forecast_days == 7:
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric&lang=ru"
            )
            data = r.json()
            forecast_data = []

            # Get current date and time
            current_date = datetime.datetime.now().date()

            # Create a dictionary to store forecast for each day
            daily_forecast = {}

            # Find weather data for the specified number of days
            for forecast in data['list']:
                forecast_date = datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S').date()
                if (forecast_date - current_date).days < forecast_days + 1:
                    date_str = forecast_date.strftime("%Y-%m-%d")
                    if date_str not in daily_forecast:
                        daily_forecast[date_str] = []
                    daily_forecast[date_str].append({
                        'time': datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M"),
                        'temp': forecast['main']['temp'],
                        'description': forecast['weather'][0]['description']
                    })

            forecast_message = f"<b>Прогноз погоды в городе {city} на {forecast_days} дней:</b>\n\n"

            # Output forecast for each day separately
            for date, forecasts in daily_forecast.items():
                forecast_message += f"<b>{date}:</b>\n"
                for forecast in forecasts:
                    emoji = weather_emojis.get(forecast['description'], "")
                    forecast_message += f"{forecast['time']} : ☑ {forecast['temp']}°C - {emoji} {forecast['description']}\n"
                forecast_message += "\n"

            await bot.send_message(callback_query.from_user.id, forecast_message, parse_mode="HTML")

    except Exception as ex:
        await bot.send_message(callback_query.from_user.id, "Ошибка при получении прогноза погоды")

async def on_startup(_):
    asyncio.create_task(hourly_weather_notifications())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)