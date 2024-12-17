import requests
import json
import random
import telebot
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


TOKEN = "6854013673:AAEwgPkyuEfCR76uZfY276VP23aVD_UIcl8"
GOOGLE_API_KEY = 'AIzaSyAqEKOKf6iPtY7q_ka18nwbMdwvohK6j6A'
GOOGLE_CX = 'f31918ec8b418499b'


image_path = "/content/photo.jpg"
with open('/content/drive/MyDrive/ASUtest/city.list.json', 'r') as file:
    cityLists = json.load(file)

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

bot = telebot.TeleBot(TOKEN)



def weather_request(town):
  return 'https://api.openweathermap.org/data/2.5/weather?q=' + town + '&appid=28e430af1640c007d30dbe021c9a8a2d&units=metric&lang=Ru'

def weather_request_id(cityId):
  return 'https://api.openweathermap.org/data/2.5/weather?id=' + str(cityId) +'&appid=28e430af1640c007d30dbe021c9a8a2d&units=metric&lang=Ru'

def generate_caption(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    generated_ids = model.generate(**inputs)
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    return caption

def search_similar_images(api_key, cse_id, message):
    service = build("customsearch", "v1", developerKey=api_key)
    try:
        res = service.cse().list(
            q=generate_caption(image_path),
            cx=cse_id,
            searchType='image',
            num=10
        ).execute()
        image_urls = [item['link'] for item in res.get('items', [])]
        return image_urls
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def send_images(chat_id, image_urls):
    media_group = []
    for url in image_urls:
        media_group.append(telebot.types.InputMediaPhoto(url))

    bot.send_media_group(chat_id, media_group)

@bot.message_handler(commands=['start'])
def send_start(message):
	bot.send_message(message.chat.id, "Привет, я погоднокартиночный бот! Напиши /help чтобы узнать мои команды.")

@bot.message_handler(commands=['help'])
def send_help(message):
	bot.send_message(message.chat.id, "Справка:\n /barnaul - показывает текущую погоду в Барнауле.\n /weather <Название города> - показывает погоду в выбранном городе\n /compare <Названия городов> - сравнивает влажность в разных городах\n /random - показывает погоду в случайном городе\n\nА если отправить мне картинку я постараюсь скинуть тебе 10 похожих.")

@bot.message_handler(commands=['barnaul'])
def send_weather_Barnaul(message):
  response = requests.get(weather_request('Barnaul'))
  if response.status_code == 200:
    data = response.json()

    bot.send_message(message.chat.id, f"Выбранный Вами город: {data.get('name')}\n\nПогода: {data.get('weather', [{}])[0].get('description')}\nТемпература: {data.get('main', {}).get('temp')}°С\nОщущается как: {data.get('main', {}).get('feels_like')}°С\nМинимальная: {data.get('main', {}).get('temp_min')}°С\nМаксимальная: {data.get('main', {}).get('temp_max')}°С\nВлажность: {data.get('main', {}).get('humidity')}%\nДавление: {data.get('main', {}).get('pressure')} мм рт. ст.\nСкорость ветра: {data.get('wind', {}).get('speed')} м/c\n")
  else:
    bot.send_message(message.chat.id, f"Ошибка при выполнении запроса: {response.status_code}")

@bot.message_handler(commands=['random'])
def send_weather_random(message):
  CityIds = [item['id'] for item in cityLists]
  response = requests.get(weather_request_id(random.choice(CityIds)))
  if response.status_code == 200:
    data = response.json()

    bot.send_message(message.chat.id, f"Выбранный Вами город: {data.get('name')}\n\nПогода: {data.get('weather', [{}])[0].get('description')}\nТемпература: {data.get('main', {}).get('temp')}°С\nОщущается как: {data.get('main', {}).get('feels_like')}°С\nМинимальная: {data.get('main', {}).get('temp_min')}°С\nМаксимальная: {data.get('main', {}).get('temp_max')}°С\nВлажность: {data.get('main', {}).get('humidity')}%\nДавление: {data.get('main', {}).get('pressure')} мм рт. ст.\nСкорость ветра: {data.get('wind', {}).get('speed')} м/c\n")
  else:
    bot.send_message(message.chat.id, f"Ошибка при выполнении запроса: {response.status_code}")

@bot.message_handler(commands=['weather'])
def send_weather_Town(message):
    args = message.text.split()[1:]
    if not args:
        help_text = (
            "Использование команды /weather:\n"
            "/weather [город]\n"
            "Пример: /weather Барнаул"
        )
        bot.send_message(message.chat.id, help_text)
    else:
        city = ' '.join(args)
        response = requests.get(weather_request(city))
        if response.status_code == 200:
          data = response.json()

          bot.send_message(message.chat.id, f"Выбранный Вами город: {data.get('name')}\n\nПогода: {data.get('weather', [{}])[0].get('description')}\nТемпература: {data.get('main', {}).get('temp')}°С\nОщущается как: {data.get('main', {}).get('feels_like')}°С\nМинимальная: {data.get('main', {}).get('temp_min')}°С\nМаксимальная: {data.get('main', {}).get('temp_max')}°С\nВлажность: {data.get('main', {}).get('humidity')}%\nДавление: {data.get('main', {}).get('pressure')} мм рт. ст.\nСкорость ветра: {data.get('wind', {}).get('speed')} м/c\n")
        else:
          bot.send_message(message.chat.id, f"Ошибка при выполнении запроса, возможно было введено название с ошибкой или сразу несколько городов. Статус: {response.status_code}")

@bot.message_handler(commands=['about'])
def handle_about(message):
  bot.send_photo(message.chat.id, "https://sun9-80.userapi.com/impf/c851136/v851136988/1061aa/boTLclsDmHI.jpg?size=2560x1707&quality=96&sign=256c2921bbd5bc9641d1deb3caccb71e&type=album", "Бота создал Плахотнюк Роман Максимович студент второго курса АГУ, из группы 5.205.2\nОбратная связь через вконтакте vk.com/id453485745")

@bot.message_handler(commands=['compare'])
def send_weather_compare(message):
    text = message.text.replace('/compare', '').strip()
    if not text:
        bot.send_message(message.chat.id, "Пожалуйста, введите города через запятую после команды /compare. Например: /compare Барнаул, Томская область, Новосибирск")
    else:
        cities = [city.strip() for city in text.split(',')]
        print(cities)
        print(type(cities))
        if len(cities) == 1:
            bot.send_message(message.chat.id, "Пожалуйста, введите еще один город через запятую. Например: /compare Барнаул, Томская область")
        else:
            humidity_dict = {}
            humidityList = "Относительная влажность в выбраных городах:\n"
            for town in cities:
              response = requests.get(weather_request(town))
              if response.status_code == 200:
                data = response.json()
                humidity_dict[data.get('name')] = data.get('main', {}).get('humidity')
                humidityList += f"Г. {data.get('name')} = {data.get('main', {}).get('humidity')}%\n"
              else:
                bot.send_message(message.chat.id, f"Название города: {town} - содержит ошибку, оно было автоматические исключено из сравнения")
            bot.send_message(message.chat.id, f"{humidityList}\nНаименьшая из низ {humidity_dict[min(humidity_dict, key=humidity_dict.get)]}% в городе {min(humidity_dict, key=humidity_dict.get)}")


@bot.message_handler(content_types=['photo'])
def photo_search(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('photo.jpg', 'wb') as new_file:
      new_file.write(downloaded_file)
    waiter = bot.reply_to(message, "Ищу похожие картинки, минуточку")
    try:
      send_images(message.chat.id, search_similar_images(GOOGLE_API_KEY, GOOGLE_CX, message))
      bot.delete_message(chat_id=message.chat.id, message_id=waiter.message_id)
    except:
      bot.delete_message(chat_id=message.chat.id, message_id=waiter.message_id)
      bot.send_message(message.chat.id, "Ничего не найдено")

bot.infinity_polling()
