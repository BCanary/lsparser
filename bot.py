import telebot
import sqlite3
import random
import time

TOKEN = ""
bot = telebot.TeleBot(TOKEN);

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('скриншот')

users = []
chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
	's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

def logger(msg):
	named_tuple = time.localtime() # получить struct_time
	time_log = str(time.strftime("%m/%d/%Y", named_tuple))
	time_log = time_log.replace("/", "-")
	try:
		with open("logs/log[" + time_log + "].log", "a") as log:
			pass
	except:
		with open("logs/log[" + time_log + "].log", "w") as log:
		 	pass

	with open("logs/log[" + time_log + "].log", "a") as log:
		mt = str(time.strftime("%H:%M:%S", named_tuple))
		log.write("[" + mt + "]" + msg + "\n")
	print("[" + mt + "]" + msg)


logger("Bot starting...")

class User():
	def __init__(self, id):
		global logger
		logger("Подключился юзер: " + str(id))

		url = 'roczuy'
		with sqlite3.connect("lsparser.db") as conn:
			cursor = conn.cursor()
			cursor.execute(f"SELECT * FROM players WHERE ID={id};")
			reusult = cursor.fetchall()
			print(reusult)
			if reusult == []:
				cursor.execute(f"INSERT INTO players VALUES ({id}, \'roczuy\');")
				logger("юзер не зарегестрирован, регестрируем...\n")
			else:
				logger("юзер зарегестрирован!\n")
				url = tuple(reusult[0])[1]
			conn.commit()

		self.id = id
		self.url = url

	def next_url(self):
		global chars

		with sqlite3.connect("lsparser.db") as conn:
			cursor = conn.cursor()
			cursor.execute(f"SELECT * FROM players WHERE ID={self.id};")
			reusult = cursor.fetchall()
			url = tuple(reusult[0])[1]
			if(self.url != url):
				logger(str(self.id) + ": " + "url изменен" )
			self.url = url

		url = list(self.url)
		url_symbol_index = -1

		while True:
			next_index = chars.index(url[url_symbol_index]) + 1
			if(next_index >= len(chars) - 1):
				url[url_symbol_index] = "a"
				url_symbol_index -= 1
			else:
				url[url_symbol_index] = chars[next_index]
				break

		self.url = "".join(url)
		with sqlite3.connect("lsparser.db") as conn:
			cursor = conn.cursor()
			
			cursor.execute(f"UPDATE players SET url = \'{self.url}\' WHERE id = {self.id}")
			
			conn.commit()

with sqlite3.connect("lsparser.db") as conn:
	cursor = conn.cursor()
			
	cursor.execute(f"SELECT * FROM players")
	all_users_bd = cursor.fetchall()
			
	conn.commit()

for i in all_users_bd:
	users.append(User(i[0]))



@bot.message_handler(commands=['start'])
def start_message(message):
	global users
	user = "None"
	for i in users:
		if i.id == message.chat.id:
			user = i

	if user == "None":
		user = User(message.chat.id)
		users.append(user)

	bot.send_message(message.chat.id, 'Добро пожаловать в парсер скринов!\nнаписав скриншот вы получите следующий скриншот,\nнаписав /url abc123 вы перейдете на этот url.', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
	global users

	user = "None"
	for i in users:
		if i.id == message.chat.id:
			user = i

	if user == "None":
		user = User(message.chat.id)
		users.append(user)

	#-----------LOGS----------
	logger(message.chat.first_name + "(" + str(user.id) + "):" + message.text)
	#--------------------------

	if "/url" in message.text:
		try:
			newurl = message.text.split(" ")[1]
		except:
			bot.send_message(message.chat.id, "Ошибка! Введите 6 значный url после комманды a-z 0-9! (/url abc123)")
		else:
			bot.send_message(message.chat.id, "Url изменен на - " + newurl)
			with sqlite3.connect("lsparser.db") as conn:
				cursor = conn.cursor()
				
				cursor.execute(f"UPDATE players SET url = \'{newurl}\' WHERE id = {message.chat.id}")
				
				conn.commit()
			user.next_url()
			url = "http://prntscr.com/" + user.url
			bot.send_message(message.chat.id, url, reply_markup=keyboard1)


	elif message.text.lower() == "скриншот":
		user.next_url()
		url = "http://prntscr.com/" + user.url
		bot.send_message(message.chat.id, url, reply_markup=keyboard1)
	else:
		bot.send_message(message.chat.id, "Введите коректную команду - скриншот или /url ", reply_markup=keyboard1)


bot.polling()