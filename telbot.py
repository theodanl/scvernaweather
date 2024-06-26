import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import requests
import datetime

bot = Bot(token='6964370519:AAETLP2uaIyHbtpp3JRaoeqKlIAH7mm6bsc')
dp = Dispatcher(bot)

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Установить город'))

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
        emoji = weather_emojis.get(description, '')  # Get emoji for weather description

        if temp < -25:
            result = 'Слишком холодно! Не выходите без крайней необходимости. Если вы все-таки выходите, наденьте очень теплую одежду, шарф, перчатки и головной убор.'
            image_path = "./images/очень_холодно.jpg"
        elif temp < 0:
            result = 'Холодно! Наденьте теплую куртку, шапку и перчатки. Постарайтесь не оставаться на улице долгое время.'
            image_path = "./images/холодно.jpg"
        elif temp < 10:
            result = 'Прохладно! Рекомендуется надеть теплую куртку или свитер с шарфом. Обувь должна быть удобной и теплой.'
            image_path = "./images/прохладно.jpg"
        elif temp < 20:
            result = 'Тепло! Оденьтесь соответственно, чтобы вам было комфортно на улице. Можете взять с собой легкую куртку на всякий случай.'
            image_path = "./images/тепло.jpg"
        elif temp < 30:
            result = 'Жарко! Рекомендуется носить легкую одежду из натуральных материалов, чтобы избежать перегрева.'
            image_path = "./images/жарко.jpg"
        else:
            result = 'Очень жарко! Оставайтесь в тени, пейте больше воды и носите легкую, свободную одежду из натуральных тканей.'
            image_path = "./images/очень_жарко.jpg"

        # Формируем текст сообщения
        message_text = f"<b>Сейчас в городе {city}</b>\n\n"\
                       f"<i>Температура:</i> {temp}°C\n"\
                       f"<i>Погода:</i> {description} {emoji}\n"\
                       f"<i>Рекомендации:</i> {result}\n"

        # Отправляем сообщение с изображением и текстом
        with open(image_path, "rb") as photo_file:
            await bot.send_photo(
                chat_id,
                photo=photo_file,
                caption=message_text,
                parse_mode="HTML"
            )

    except Exception as ex:
        await bot.send_message(chat_id, f"Ошибка при получении погоды для города {city}: {ex}")

async def hourly_weather_notifications():
    while True:
        await asyncio.sleep(300)  # Ожидание 1 часа
        for chat_id, city in default_city.items():
            await send_hourly_weather_notification(city, chat_id)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Приветственное сообщение
    welcome_message = "Привет! Я - бот, который предоставляет информацию о погоде. Для начала выбери свой основной город."

    # Красивое меню
    start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text='Установить город'))

    # Отправляем приветственное сообщение с локальным изображением
    with open('./images/logo_preview.jpg', 'rb') as photo:
        await message.answer_photo(photo=photo, caption=welcome_message, reply_markup=start_keyboard)

@dp.message_handler(text='Установить город')
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
        
        # Check if the user is in the process of setting the city
        if message.from_user.id in user_city:
            city = message.text
            
            r = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={open_weather_token}&units=metric"
            )
            data = r.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            weather_type = data['weather'][0]['main']
            emoji = weather_emojis.get(description, "")
            
            if temp < -25:
                result = 'Очень холодно, лучше всего остаться дома.'
                image_path = "./images/очень_холодно.jpg"
            elif temp < 0:
                result = 'Холодно, одевайтесь теплее.'
                image_path = "./images/холодно.jpg"
            elif temp < 10:
                result = 'Прохладно, лучше надеть куртку.'
                image_path = "./images/прохладно.jpg"
            elif temp < 20:
                result = 'Тепло, на улице приятно.'
                image_path = "./images/тепло.jpg"
            elif temp < 30:
                result = 'Жарко, можете надеть что-то легкое.'
                image_path = "./images/жарко.jpg"
            else:
                result = 'Очень жарко, наденьте что-то легкое и пейте воду.'
                image_path = "./images/очень_жарко.jpg"
                
            # Формируем текст сообщения
            message_text = f"<b>Сейчас в городе {city}</b>\n\n"\
                           f"<i>Температура:</i> {temp}°C\n"\
                           f"<i>Погода:</i> {description} {emoji}\n"\
                           f"<i>Рекомендации:</i> {result}\n"
            
            # Отправляем сообщение с изображением и текстом
            with open(image_path, "rb") as photo_file:
                await bot.send_photo(
                    message.chat.id,
                    photo=photo_file,
                    caption=message_text,
                    parse_mode="HTML"
                )

            # Добавляем клавиатуру для выбора прогноза погоды
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Погода на 1 день", callback_data=f"weather_forecast_1_{city}"))
            keyboard.add(types.InlineKeyboardButton(text="Погода на 3 дня", callback_data=f"weather_forecast_3_{city}"))
            keyboard.add(types.InlineKeyboardButton(text="Погода на 7 дней", callback_data=f"weather_forecast_7_{city}"))
            await bot.send_message(message.from_user.id, "Выберите интересующий вас прогноз погоды:", reply_markup=keyboard)
            
            # Сохраняем выбранный пользователем город как его основной
            default_city[message.from_user.id] = city
            
            # Удаляем пользователя из временного словаря, так как город уже установлен
            del user_city[message.from_user.id]
        
        else:
            await bot.send_message(message.from_user.id, "Проверьте название города")

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