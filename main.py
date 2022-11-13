import os
import os.path
import sys
import time
import datetime
import re
import logging
import subprocess
import geocoder
import requests
import random
import traceback
import json
import html
import hashlib
import base64
from captcha.image import ImageCaptcha
from typing import Optional, Tuple
from traceback import format_exc as F_err
from random import randrange, choice
from html import escape
from uuid import uuid4

from telegram import __version__ as TG_VER

try:
	from telegram import __version_info__
except ImportError:
	__version_info__ = (0, 0, 0, 0, 0)  #Type: ignore[assignment]

class bcolors:
	PINK = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	GRAY = '\033[90m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	NEGATIVE1 = '\033[3m'
	NEGATIVE2 = '\033[5m'
	PINKBG = '\033[45m'
	BLUEBG = '\033[44m'
	CYANBG = '\033[46m'
	GREENBG = '\033[42m'
	YELLOWBG = '\033[43m'
	REDBG = '\033[41m'
	GRAYBG = '\033[47m'
	
class clogs:
	INFO = '\033[96m'
	WARNING = '\033[93m'
	ERROR = '\033[91m'
	CRITICAL = '\033[41m'
	DEBUG = '\033[95m'
	BOLD = '\033[1m'
	ENDC = '\033[0m'

if __version_info__ < (20, 0, 0, "alpha", 1):
	import webbrowser
	webbrowser.open(f'https://docs.python-telegram-bot.org/en/v{TG_VER}')
	raise RuntimeError(
		f"\n\n"
		f""+bcolors.RED+""
		f"ERROR | It's look like your PTB version {TG_VER} < 20\n"
		f""+bcolors.CYAN+""
		f'INFO | Visit "https://docs.python-telegram-bot.org/en/v{TG_VER}/"'
		f""+bcolors.ENDC+""
	)

from telegram import ForceReply, Chat, ChatMember, ChatMemberUpdated, WebAppInfo, InlineKeyboardButton, InlineQueryResultArticle, InlineKeyboardMarkup, LabeledPrice, ShippingOption, InputTextMessageContent, Update, helpers
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, InlineQueryHandler, CommandHandler, ContextTypes, MessageHandler, ChatMemberHandler, filters, PreCheckoutQueryHandler, ShippingQueryHandler, ConversationHandler

print(bcolors.CYAN+'INFO | Please wait...')


#botinfo
onUpdate = False
intversion = 1
version = "V1"
pid = "Unkown"
starttime = time.time()
uptime = time.time() - starttime
imports = [m.__name__ for m in sys.modules.values() if m]
botevents = []

#permissions
ownerID = 0 #Write your own id
adminID = [0] #Write admin ids
logchannel = ownerID #Write channel id to log

#Tokens
TelegramBotToken = '0' #Write your telegram bot token
DonatelloToToken = "0" #Write your payment tokens

#Check info about script, device, host
restartsec = 0
def infocheck():
	global restartsec
	global pid
	from progress.bar import Bar
	from datetime import datetime
	print(bcolors.BLUE + bcolors.BOLD)
	checking = Bar('INFO | Checking...', max=100, fill='=', suffix='%(index)d%% | %(eta)ds')
	for i in range(100):
		time.sleep(random.uniform(0.001, 0.01))
		checking.next()
	try:
		pypiget = requests.get('https://pypi.org/rss/project/python-telegram-bot/releases.xml')
	except:
		print(bcolors.RED + "\nERROR | Internet connection error! Restarting in "+str(restartsec)+" seconds...")
		restartsec += 1
		time.sleep(restartsec)
		infocheck()
	pypitext = pypiget.text
	pypisplit = pypitext.split('\n')
	pypiver = pypisplit[8]
	pypilink = pypisplit[9]
	pypiver = pypiver.replace("<title>", "")
	pypiver = pypiver.replace("</title>", "")
	pypiver = pypiver.replace(" ", "")
	pypilink = pypilink.replace("<link>", "")
	pypilink = pypilink.replace("</link>", "")
	pypilink = pypilink.replace(" ", "")
	try:
		int(float(pypiver))
		if int(float(pypiver)) < 20.00:
			pypiver = TG_VER
	except:
		pypiver = pypiver
	print(bcolors.ENDC + bcolors.CYAN + '\n\nINFO | ' + str(os.uname()))
	print(bcolors.ENDC + bcolors.CYAN + 'INFO | Imports: ' + bcolors.BOLD + str(len(imports)))
	if TG_VER == pypiver:
		print(bcolors.ENDC + bcolors.CYAN + 'INFO | Python-Telegram-Bot Version: ' + bcolors.BOLD + TG_VER + bcolors.ENDC + bcolors.GREEN + ' (Latest)')
	else:
		print(bcolors.ENDC + bcolors.CYAN + 'INFO | Python-Telegram-Bot Version: ' + bcolors.BOLD + TG_VER + bcolors.ENDC + bcolors.YELLOW + ' (' + pypiver + ' available)')
		print(bcolors.ENDC + bcolors.BLUE + 'LINK | ' + pypilink + '')
		print(bcolors.ENDC + bcolors.BLUE + 'LINK | https://docs.python-telegram-bot.org/en/' + pypiver + '/')
	print(bcolors.ENDC + bcolors.CYAN + 'INFO | Bot Version: ' + bcolors.BOLD + str(version))
	if os.path.exists("database.json") == False:
		print(bcolors.ENDC + bcolors.YELLOW + 'INFO | database.json not founded')
		data_create = open("database.json","w")
		data_create.write("{}")
		data_create.close()
		print(bcolors.ENDC + bcolors.GREEN + 'INFO | database.json created and saved')
	else:
		filestats = os.stat("database.json")
		try:
			data = json.loads(open("database.json","r").read())
			print(bcolors.ENDC + bcolors.CYAN + 'INFO | database.json '+bcolors.BOLD+'('+str(filestats.st_size)+'B)'+bcolors.ENDC+bcolors.CYAN+' founded and loaded')
		except:
			print(bcolors.ENDC + bcolors.YELLOW + 'WARNING | database.json '+bcolors.BOLD+'('+str(filestats.st_size)+'B)'+bcolors.ENDC+bcolors.YELLOW+' not loaded!')
			time.sleep(5)
	if os.path.exists("shop.json") == False:
		print(bcolors.ENDC + bcolors.YELLOW + 'INFO | shop.json not founded')
		data_create = open("shop.json","w")
		x = {
			"items":{
				"item":[],
				"price":[],
				"discount":[],
				"amount":[],
				"com":[],
				"purchase":[]
			},
			"codes":{
				"code":[],
				"value":[],
				"amount":[],
				"com":[]
			},
			"payment":{
				"list":[],
				"enabled":[]
			},
		}
		json.dump(x, open("shop.json","w"))
		print(bcolors.ENDC + bcolors.GREEN + 'INFO | shop.json created and saved')
	else:
		filestats = os.stat("shop.json")
		try:
			data = json.loads(open("shop.json","r").read())
			print(bcolors.ENDC + bcolors.CYAN + 'INFO | shop.json '+bcolors.BOLD+'('+str(filestats.st_size)+'B)'+bcolors.ENDC+bcolors.CYAN+' founded and loaded\n')
		except:
			print(bcolors.ENDC + bcolors.YELLOW + 'WARNING | shop.json '+bcolors.BOLD+'('+str(filestats.st_size)+'B)'+bcolors.ENDC+bcolors.YELLOW+' not loaded!\n')
			time.sleep(5)
	if os.path.exists("stock.json") == False:
		print(bcolors.ENDC + bcolors.YELLOW + 'INFO | stock.json not founded')
		data_create = open("stock.json","w")
		x = {
			"X":[""],
		}
		json.dump(x, open("stock.json","w"))
		print(bcolors.ENDC + bcolors.GREEN + 'INFO | stock.json created and saved')
	else:
		filestats = os.stat("stock.json")
		try:
			data = json.loads(open("stock.json","r").read())
			print(bcolors.ENDC + bcolors.CYAN + 'INFO | stock.json '+bcolors.BOLD+'('+str(filestats.st_size)+'B)'+bcolors.ENDC+bcolors.CYAN+' founded and loaded\n')
		except:
			print(bcolors.ENDC + bcolors.YELLOW + 'WARNING | stock.json '+bcolors.BOLD+'('+str(filestats.st_size)+'B)'+bcolors.ENDC+bcolors.YELLOW+' not loaded!\n')
			time.sleep(5)
	try:
		os.getlogin()
		pid = str(os.getpid())
	except:
		pid = 'Hosted'
	print(bcolors.GREEN + "\nINFO | All correct!")
	print(bcolors.ENDC)

infocheck()

def containsNumber(value):
	for character in value:
		if character.isdigit():
			return True
	return False

def is_integer_num(n):
	if isinstance(n, int):
		return True
	if isinstance(n, float):
		return n.is_integer()
	return False



#Enable logging
logformatI = clogs.BOLD+"%(levelname)s | %(asctime)s | %(name)s - %(message)s"+clogs.ENDC
logformatW = clogs.BOLD+clogs.WARNING+"%(levelname)s | %(asctime)s | %(name)s - %(message)s"+clogs.ENDC
logformatE = clogs.BOLD+clogs.ERROR+"%(levelname)s | %(asctime)s | %(name)s - %(message)s"+clogs.ENDC
logformatC = clogs.BOLD+clogs.CRITICAL+"%(levelname)s | %(asctime)s | %(name)s - %(message)s"+clogs.ENDC
logformatD = clogs.BOLD+clogs.DEBUG+"%(levelname)s | %(asctime)s | %(name)s - %(message)s"+clogs.ENDC

logging.basicConfig(
	format=logformatI, level=logging.INFO
)
logging.basicConfig(
	format=logformatW, level=logging.WARNING
)
logging.basicConfig(
	format=logformatE, level=logging.ERROR
)
logging.basicConfig(
	format=logformatC, level=logging.CRITICAL
)
logging.basicConfig(
	format=logformatD, level=logging.DEBUG
)
logger = logging.getLogger(__name__)



#Define a few command handlers. These usually take the two arguments update and context.

if onUpdate == True:
			async def onUpdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
				await update.message.reply_text(f'🔨 *{context.bot.first_name}* is on update.\n🕓 Wait some time!\n⚙️ Version: *' + version + '*', parse_mode= 'Markdown')



async def querybuttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	keyboard = [
		[
			InlineKeyboardButton("0", callback_data="0"),
			InlineKeyboardButton("1", callback_data="1"),
			InlineKeyboardButton("2", callback_data="2"),
		],
		[
			InlineKeyboardButton("3", callback_data="3"),
			InlineKeyboardButton("4", callback_data="4"),
			InlineKeyboardButton("5", callback_data="5"),
		],
		[
			InlineKeyboardButton("6", callback_data="6"),
			InlineKeyboardButton("7", callback_data="7"),
			InlineKeyboardButton("8", callback_data="8"),
		],
		[InlineKeyboardButton("9", callback_data="9")],
	]
	buttons = InlineKeyboardMarkup(keyboard)
	
	query = update.callback_query
	await query.answer()
	if query.data == 'profile':
		user = str(query.from_user.id)
		us = query.from_user
		data = json.loads(open("database.json","r").read())
		balance = data[user]["balance"]
		transaction = data[user]["transactions"]
		item = transaction["item"]
		price = transaction["price"]
		item = item[len(item)-1]
		price = price[len(price)-1]
		lang = data[user]["lang"]
		if lang == 'ru':
			refill = "Пополнить баланс"
			shop = "Магазин"
			settings = "Настройки"
			text = f'🌀 Твой профиль\n👤 Ник: <b>{us.username}</b>\n🆔 Айди: <b>{us.id}</b>\n💳 Баланс: <b>{balance}</b>₴\n📑 Последняя транзакция: <b>{item}</b> ({price}₴)\n🇷🇺 Язык: <b>{lang}</b>'
		elif lang == 'uk':
			refill = "Поповнити баланс"
			shop = "Магазин"
			settings = "Налаштування"
			text = f'🌀 Твій профіль\n👤 Нік: <b>{us.username}</b>\n🆔 Айді: <b>{us.id}</b>\n💳 Баланс: <b>{balance}</b>₴\n📑 Остання транзакція: <b>{item}</b> ({price}₴)\n🇺🇦 Мова: <b>{lang}</b>'
		else:
			refill = "Refill balance"
			shop = "Shop"
			settings = "Settings"
			text = f'🌀 Your profile\n👤 Nickname: <b>{us.username}</b>\n🆔 ID: <b>{us.id}</b>\n💳 Balance: <b>{balance}</b>₴\n📑 Last transaction: <b>{item}</b> ({price}₴)\n🇺🇸 Language: <b>{lang}</b>'
		profilekeyboard = [
			[InlineKeyboardButton(f"💸 {refill}", callback_data="refillbalance")],
			[InlineKeyboardButton(f"🛍 {shop}", callback_data="shop")],
			[InlineKeyboardButton(f"⚙️ {settings}", callback_data="settings")],
		]
		profilebuttons = InlineKeyboardMarkup(profilekeyboard)
		await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=profilebuttons)
	if query.data == 'refillbalance':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = "Выберите способ оплаты"
			s_back = "Назад"
		elif lang_data == 'uk':
			text = "Оберіть спосіб оплати"
			s_back = "Назад"
		else:
			text = "Select a payment method"
			s_back = "Back"
		data_shop = json.loads(open("shop.json","r").read())
		keyboard = []
		for i in range(len(data_shop["payment"]["list"])):
			l = data_shop["payment"]["list"][i]
			if data_shop["payment"]["enabled"][i] == "True":
				if l == "donatello":
					keyboard += [
						[InlineKeyboardButton(f"🇺🇦 Donatello", callback_data="r_donatello")],
					]
				else:
					keyboard += [
						[InlineKeyboardButton(f"🇦🇦 {l.title()}", callback_data=f"r_{l}")],
					]
		keyboard += [
			[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"💸 {text}", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 'r_donatello':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = f"Перейдите по ссылке ниже и оплатите указав в имени пользователя ваш *айди*! Ваш айди: `{user}`"
			s_check = "Проверить мой платëж"
			s_cancel = "Отменить"
			wait = "Подождите"
		elif lang_data == 'uk':
			text = f"Перейдіть по посиланню нижче та сплатіть вказав у імені користувача ваш *айді*! Ваш айді: `{user}`"
			s_check = "Перевірити мій платіж"
			s_cancel = "Відмінити"
			wait = "Зачекайте"
		else:
			text = f"Follow the link below and pay with your *ID* in your username! Your ID: `{user}`"
			s_check = "Check my payment"
			s_cancel = "Cancel"
			wait = "Wait"
		await query.edit_message_text(f"🕓 {wait}...", parse_mode='Markdown')
		data = {
			"X-Token":DonatelloToToken,
		}
		req = requests.get('https://donatello.to/api/v1/me', headers=data)
		t = json.loads(req.text)
		link = t["page"]
		keyboard = [
			[InlineKeyboardButton(f"✅ {s_check}", callback_data=f"r_check_{query.data}")],
			[InlineKeyboardButton(f"❎ {s_cancel}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"💸 {text}\n🔗 {link}", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 'shop':
		if "_p" in query.data:
			qdata = query.data
			qdsplit = qdata.split('_')
			q1 = qdsplit[0]
			q2 = qdsplit[1]
			shop_page = q2
		else:
			shop_page = "1"
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = "Выберите товар"
			TTamount = "Кол-во"
			NoneItems = "В данный момент товаров нету, приходите позже"
			s_back = "Назад"
		elif lang_data == 'uk':
			text = "Оберіть товар"
			TTamount = "Кіль-сть"
			NoneItems = "В цей час товарів немає, приходьте пізніше"
			s_back = "Назад"
		else:
			text = "Select an item"
			TTamount = "Amount"
			NoneItems = "At this time items is nothing, come back later"
			s_back = "Back"
		shop_data = json.loads(open("shop.json","r").read())
		shop = shop_data["items"]
		am = 0
		TTitems = ''
		keyboard = []
		for i in range(len(shop_data["items"]["item"])):
			Sitem = shop_data["items"]["item"][i]
			if Sitem == "":
				if lang_data == 'ru':
					TTitems = "В данный момент товаров нету, приходите позже"
				elif lang_data == 'uk':
					TTitems = "В цей час товарів немає, приходьте пізніше"
				else:
					TTitems = "At this time items is nothing, come back later"
				keyboard = [
					[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="profile")],
				]
				buttons = InlineKeyboardMarkup(keyboard)
				await query.edit_message_text(f"🛍 {TTitems}", parse_mode=ParseMode.HTML, reply_markup=buttons)
				return
			i = i*int(shop_page)
			Sprice = shop_data["items"]["price"][i]
			Sdiscount = shop_data["items"]["discount"][i]
			Samount = shop_data["items"]["amount"][i]
			Scom = shop_data["items"]["com"][i]
			am = i
			if Samount != 0:
				if am*int(shop_page) == 10*int(shop_page):
					if int(shop_page) > 1:
						keyboard += [
							[InlineKeyboardButton(f"«", callback_data="shop_p{str(int(shop_page)-1)}")],
						]
					if int(shop_p)*10 <= len(shop_data["items"]["item"]):
						keyboard += [
							[InlineKeyboardButton(f"»", callback_data="shop_p{str(int(shop_page)+1)}")],
						]
						break
				elif int(shop_page) > 1:
					keyboard += [
						[InlineKeyboardButton(f"«", callback_data="shop_p{str(int(shop_page)-1)}")],
					]
				else:
					pass
				mj = ''+random.choice(list('🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🥬🥒🌶🫑🌽🥕🫒🧄🧅🥔🍠🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🦴🌭🍔🍟🍕🫓🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼🫖☕️🍵🧃🥤🧋🍶🍺🥂🍷🥃🍸🍹🧉🍾🧊🧂'))
				TTitems += f"\n{str(am+1)}. <b>{Sitem}</b> - "
				if Sdiscount == 0:
					TTitems += f"<b>{Sprice}₴</b>"
				else:
					TTitems += f"<b>{Sprice}₴</b> <i>(-{Sdiscount}%)</i>"
				if Samount != -1:
					TTitems += f" | {TTamount}: <b>{Samount}</b>"
				if Scom != "":
					TTitems += f" | <i>{Scom}</i>"
				keyboard += [
					[InlineKeyboardButton(f"{str(mj)} {str(Sitem)} ({str(Sprice)}₴)", callback_data=f"shop_ask_item_{str(i)}")],
				]
		keyboard += [
			[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"🛍 {text}{TTitems}", parse_mode=ParseMode.HTML, reply_markup=buttons)
	if "shop_ask_item_" in query.data:
		qdata = query.data
		qdsplit = qdata.split('_')
		q1 = qdsplit[0]
		q2 = qdsplit[1]
		q3 = qdsplit[2]
		q4 = qdsplit[3]
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		shop_data = json.loads(open("shop.json","r").read())
		q4 = int(q4)
		Sitem = shop_data["items"]["item"][q4]
		Sprice = shop_data["items"]["price"][q4]
		Sdiscount = shop_data["items"]["discount"][q4]
		Samount = shop_data["items"]["amount"][q4]
		Scom = shop_data["items"]["com"][q4]
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = f"Вы уверены что хотите приобрести *{Sitem}* за *{str(Sprice)}₴*?"
			c_yes = "Да"
			c_no = "Нет"
			back = "Назад"
		elif lang_data == 'uk':
			text = f"Ви впевнені що хочете купити *{Sitem}* за *{str(Sprice)}₴*?"
			c_yes = "Так"
			c_no = "Ні"
			back = "Назад"
		else:
			text = f"Do you want buy *{Sitem}* for *{str(Sprice)}₴*?"
			c_yes = "Yes"
			c_no = "No"
			back = "Back"
		keyboard = [
			[InlineKeyboardButton(f"✅ {c_yes}", callback_data=f"shop_buy_item_{str(q4)}"),
			InlineKeyboardButton(f"❎ {c_no}", callback_data="shop")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"🛒 {text}", parse_mode='Markdown', reply_markup=buttons)
	if "shop_buy_item_" in query.data:
		qdata = query.data
		qdsplit = qdata.split('_')
		q1 = qdsplit[0]
		q2 = qdsplit[1]
		q3 = qdsplit[2]
		q4 = qdsplit[3]
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		shop_data = json.loads(open("shop.json","r").read())
		q4 = int(q4)
		Ubalance = data[user]["balance"]
		Utransactions = data[user]["transactions"]
		Uitem = data[user]["transactions"]["item"]
		Uprice = data[user]["transactions"]["price"]
		Udate = data[user]["transactions"]["date"]
		Sitem = shop_data["items"]["item"][q4]
		Sprice = shop_data["items"]["price"][q4]
		Sdiscount = shop_data["items"]["discount"][q4]
		Samount = shop_data["items"]["amount"][q4]
		Scom = shop_data["items"]["com"][q4]
		
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			successfully = f"*Успешно!* Вы приобрели *{Sitem}* за *{str(Sprice)}₴*!"
			error_money = "*Ошибка!* На вашем счету недостаточно средств!"
			tutorial = f"Напишите в поддержку используя */support* чтоб вам выдали покупку"
			Sbalance = f"Баланс: *{str(Ubalance-Sprice)}₴*"
			Ebalance = f"Баланс: *{str(Ubalance)}₴*"
			back = "Назад"
		elif lang_data == 'uk':
			successfully = f"*Успішно!* Ви купили *{Sitem}* за *{str(Sprice)}₴*!"
			error_money = "*Помилка!* На вашому рахунку недостатньо коштів!"
			tutorial = f"Напишіть у підтримку використовуя */support* щоб вам видали покупку"
			Sbalance = f"Баланс: *{str(Ubalance-Sprice)}₴*"
			Ebalance = f"Баланс: *{str(Ubalance)}₴*"
			back = "Назад"
		else:
			successfully = f"*Successfully!* You bought *{Sitem}* for *{str(Sprice)}₴*!"
			error_money = "*Error!* On your balance not enough money!"
			tutorial = f"Write to support using */support* to get your purchase"
			Sbalance = f"Баланс: *{str(Ubalance-Sprice)}₴*"
			Ebalance = f"Balance: *{str(Ubalance)}₴*"
			back = "Back"
		keyboard = [
			[InlineKeyboardButton(f"⬅️ {back}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		if Ubalance >= Sprice:
			from datetime import date
			today = date.today()
			today = str(today)
			Ubalance -= Sprice
			Uitem.append(Sitem)
			Uprice.append(Sprice)
			Udate.append(today)
			data[user]["balance"] = Ubalance
			data[user]["transactions"]["item"] = Uitem
			data[user]["transactions"]["price"] = Uprice
			data[user]["transactions"]["date"] = Udate
			if Samount != -1:
				shop_data["items"]["amount"][q4] -= 1
			json.dump(data, open("database.json","w"))
			json.dump(shop_data, open("shop.json","w"))
			text = f"☑️ {successfully}\n💳 {Sbalance}"
			if shop_data["items"]["purchase"][q4] == "/tutorial":
				text += f"\n\n❕ {tutorial}"
			await query.edit_message_text(f"{text}", parse_mode='Markdown', reply_markup=buttons)
		else:
			await query.edit_message_text(f"❌ {error_money}\n💳 {Ebalance}", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 'r_donatello':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = f"Перейдите по ссылке ниже и оплатите указав в имени пользователя ваш *айди*! Ваш айди: `{user}`"
			s_check = "Проверить мой платëж"
			s_cancel = "Отменить"
			wait = "Подождите"
		elif lang_data == 'uk':
			text = f"Перейдіть по посиланню нижче та сплатіть вказав у імені користувача ваш *айді*! Ваш айді: `{user}`"
			s_check = "Перевірити мій платіж"
			s_cancel = "Відмінити"
			wait = "Зачекайте"
		else:
			text = f"Follow the link below and pay with your *ID* in your username! Your ID: `{user}`"
			s_check = "Check my payment"
			s_cancel = "Cancel"
			wait = "Wait"
		await query.edit_message_text(f"🕓 {wait}...", parse_mode='Markdown')
		data = {
			"X-Token":DonatelloToToken,
		}
		req = requests.get('https://donatello.to/api/v1/me', headers=data)
		t = json.loads(req.text)
		link = t["page"]
		keyboard = [
			[InlineKeyboardButton(f"✅ {s_check}", callback_data=f"r_check_{query.data}")],
			[InlineKeyboardButton(f"❎ {s_cancel}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"💸 {text}\n🔗 {link}", parse_mode='Markdown', reply_markup=buttons)
	if "r_check_" in query.data:
		qdata = query.data
		qdsplit = qdata.split('_')
		q1 = qdsplit[1]
		q2 = qdsplit[2]
		q3 = qdsplit[3]
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		UpubId = data[user]["pubId"]
		Ubalance = data[user]["balance"]
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			wait = 'Проверяем'
			s_back = 'Назад'
			error = '*Ошибка!*'
			error_not_found = f'{error} Ничего не найдено'
			error_not_available = f'{error} Этот способ сейчас не доступен'
			error_unknown = f'{error} Неизвестная платëжная система'
		elif lang_data == 'uk':
			wait = 'Перевіряємо'
			s_back = 'Назад'
			error = '*Помилка!*'
			error_not_found = f'{error} Нічого не знайдено'
			error_not_available = f'{error} Цей спосіб на цей час не доступний'
			error_unknown = f'{error} Невідома платіжна система'
		else:
			wait = 'Checking'
			s_back = 'Back'
			error = '*Error!*'
			error_not_found = f'{error} Nothing found'
			error_not_available = f'{error} This payment is not available right now'
			error_unknown = f'{error} Unknown payment system'
		await query.edit_message_text(f"🔎 {wait}...", parse_mode='Markdown')
		ERRORQ3 = False
		warning = False
		if q3 == 'donatello':
			try:
				data = {
					"X-Token":DonatelloToToken,
				}
				req = requests.get('https://donatello.to/api/v1/donates', headers=data)
			except:
				keyboard = [
					[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="profile")],
				]
				buttons = InlineKeyboardMarkup(keyboard)
				await query.edit_message_text(f"❌ {error_unknown}", parse_mode='Markdown', reply_markup=buttons)
				return
			t = json.loads(req.text)
			content = t["content"]
			l = len(t["content"])
			err = 0
			for i in t["content"]:
				DpubId = i["pubId"]
				DclientName = i["clientName"]
				Damount = i["amount"]
				Dcurrency = i["currency"]
				if str(DclientName) != user:
					err += 1
				else:
					break
			keyboard = [
				[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="profile")],
			]
			buttons = InlineKeyboardMarkup(keyboard)
			if err == l:
				await query.edit_message_text(f"❌ {error_not_found}", parse_mode='Markdown', reply_markup=buttons)
				return
		else:
			ERRORQ3 = True
		if lang_data == 'ru':
			successfully = f'*Успешно!* На ваш счëт было зачислено *{Damount}*₴'
			error = '*Ошибка!*'
			error_not_found = f'{error} Ничего не найдено'
			error_qsplit = f'{error} Неизвестная платëжная система'
			error_currency = f'{error} Неизвестная валюта *{Dcurrency}*, ожидалось *UAH*'
			write = f'Сообщение об ошибке было отправлено поддержке'
			Tbalance = 'Баланс: '
		elif lang_data == 'uk':
			successfully = f'*Успішно!* На ваш рахунок було зараховано *{Damount}*₴'
			error = '*Помилка!*'
			error_not_found = f'{error} Нічого не знайдено'
			error_qsplit = f'{error} Невідома платіжна система'
			error_currency = f'{error} Невідома валюта *{Dcurrency}*, очикувалась *UAH*'
			write = f'Повідомлення об помилке було відправлено підтримці'
			Tbalance = 'Баланс: '
		else:
			successfully = f'*Successfully!* On your account has been added *{Damount}*₴'
			error = '*Error!*'
			error_not_found = f'{error} Nothing found'
			error_qsplit = f'{error} Unknown payment system'
			error_currency = f'{error} Unknown currency *{Dcurrency}*, waited for *UAH*'
			write = f'Message with error sended to support'
			Tbalance = 'Balance: '
		if ERRORQ3 == True:
			await query.edit_message_text(f"❌ {error_qsplit}", parse_mode='Markdown', reply_markup=buttons)
			return
		else:
			if Dcurrency != "UAH":
				await query.edit_message_text(f"❌ {error_currency}\n⚠️ {write}", parse_mode='Markdown', reply_markup=buttons)
				await context.bot.send_message(ownerID, text=f"⚠️ {user} payed {Damount} with unknown currency ({Dcurrency}) | Public ID: {DpubId}")
				print(bcolors.ENDC + bcolors.WARNING + 'PAYMENT | '+user+' payed '+Damount+' ('+Dcurrency+') | ID: '+DpubId+bcolors.ENDC)
				if UpubId[0] == "None":
					UpubId = [DpubId]
				else:
					UpudId.append(DpubId)
				data = json.loads(open("database.json","r").read())
				data[user]["pubId"] = UpudId
				json.dump(data, open("database.json","w"))
				return
			try:
				if str(DclientName) == user:
					if DpubId not in UpubId:
						data = json.loads(open("database.json","r").read())
						try:
							user = context.user_data["user"]
						except:
							user = str(query.from_user.id)
						data = json.loads(open("database.json","r").read())
						UpubId = data[user]["pubId"]
						Ubalance = data[user]["balance"]
						if UpubId[0] == "None":
							UpubId = [DpubId]
						else:
							UpudId.append(DpubId)
						Ubalance += int(Damount)
						data[user]["balance"] = Ubalance
						data[user]["pubId"] = UpubId
						json.dump(data, open("database.json","w"))
						data = json.loads(open("database.json","r").read())
						print(bcolors.ENDC + bcolors.CYAN + 'PAYMENT | '+user+' payed '+Damount+' ('+Dcurrency+') | ID: '+DpubId+bcolors.ENDC)
						try:
							await context.bot.send_message(ownerID, text=f'💸 Payment from *{user}* on *{str(Damount)}* _({Dcurrency})_ | ID: *{str(DpudId)}*', parse_mode='Markdown')
						except:
							await context.bot.send_message(ownerID, text=f'💸 Test Payment from *{user}* on *{str(Damount)}* _({Dcurrency})_ | ID: *Test*', parse_mode='Markdown')
						await query.edit_message_text(f"☑️ {successfully}\n💳 {Tbalance}*{str(Ubalance)}₴*\n🧾 Public ID: _{str(DpubId)}_", parse_mode='Markdown', reply_markup=buttons)
					else:
						await query.edit_message_text(f"❌ {error_not_found}", parse_mode='Markdown', reply_markup=buttons)
				else:
					await query.edit_message_text(f"❌ {error_not_found}", parse_mode='Markdown', reply_markup=buttons)
			except:
				await query.edit_message_text(f"❌ {error}\n{F_err()}", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 'settings':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = "Используйте кнопки ниже"
			s_data = "Мои данные"
			s_checkout = "Чеки"
			s_lang = "Сменить язык"
			s_codes = "Коды"
			s_back = "Назад"
		elif lang_data == 'uk':
			text = "Використовуйте кнопки нижче"
			s_data = "Мої дані"
			s_checkout = "Чеки"
			s_lang = "Змінити мову"
			s_codes = "Коди"
			s_back = "Назад"
		else:
			text = "Use buttons below"
			s_data = "My data"
			s_checkout = "Checkouts"
			s_lang = "Change language"
			s_codes = "Codes"
			s_back = "Back"
		keyboard = [
			[InlineKeyboardButton(f"🗂 {s_data}", callback_data="s_data")],
			[InlineKeyboardButton(f"🧾 {s_checkout}", callback_data="s_checkout")],
			[InlineKeyboardButton(f"🇦🇦 {s_lang}", callback_data="s_lang")],
			[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"⚙️ {text}", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 's_data':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = "Ваши данные"
			s_back = "Назад"
		elif lang_data == 'uk':
			text = "Ваші дані"
			s_back = "Назад"
		else:
			text = "Your data"
			s_back = "Back"
		keyboard = [
			[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="settings")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"🗂 {text} *({user})*\n`{str(data[user])}`", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 's_checkout':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = "Ваши чеки"
			s_back = "Назад"
		elif lang_data == 'uk':
			text = "Ваші чеки"
			s_back = "Назад"
		else:
			text = "Your checkouts"
			s_back = "Back"
		keyboard = [
			[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="settings")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		am = 0
		ck = ""
		transaction = data[user]["transactions"]
		item = transaction["item"]
		price = transaction["price"]
		date = transaction["date"]
		if len(item) <=1 and item[0] == "Registration":
			if lang_data == 'ru':
				ck = "*Вы ещë не делали покупок!*"
			elif lang_data == 'uk':
				ck = "*Ви ще нічого не купували!*"
			else:
				ck = "*You didn't buy anything!*"
		else:
			for i in item:
				am += 1
				ck += f"{str(am)}. *{str(item[am-1])}* ({str(price[am-1])}₴) | {str(date[am-1])}\n"
		await query.edit_message_text(f"🧾 {text}\n{ck}", parse_mode='Markdown', reply_markup=buttons)
	if query.data == 's_lang':
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		s_l_ru = "Русский (ru)"
		s_l_uk = "Українська (uk)"
		s_l_en = "English (en)"
		if lang_data == 'ru':
			text = "Выберите язык для смены"
			s_back = "Назад"
			keyboard = [
				[InlineKeyboardButton(f"🇺🇦 {s_l_uk}", callback_data="s_l_uk")],
				[InlineKeyboardButton(f"🇺🇸 {s_l_en}", callback_data="s_l_en")],
				[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="settings")],
			]
			buttons = InlineKeyboardMarkup(keyboard)
		elif lang_data == 'uk':
			text = "Виберіть мову для зміни"
			s_back = "Назад"
			keyboard = [
				[InlineKeyboardButton(f"🇷🇺 {s_l_ru}", callback_data="s_l_ru")],
				[InlineKeyboardButton(f"🇺🇸 {s_l_en}", callback_data="s_l_en")],
				[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="settings")],
			]
			buttons = InlineKeyboardMarkup(keyboard)
		else:
			text = "Choose language to change"
			s_back = "Back"
			keyboard = [
				[InlineKeyboardButton(f"🇷🇺 {s_l_ru}", callback_data="s_l_ru")],
				[InlineKeyboardButton(f"🇺🇦 {s_l_uk}", callback_data="s_l_uk")],
				[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="settings")],
			]
			buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"🇦🇦 {text}", parse_mode='Markdown', reply_markup=buttons)
	if "s_l_" in query.data:
		qdata = query.data
		qdsplit = qdata.split('_')
		q1 = qdsplit[0]
		q2 = qdsplit[1]
		q3 = qdsplit[2]
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		data[user]["lang"] = q3
		json.dump(data, open("database.json","w"))
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = "Язык успешно сменен на "
			s_back = "Назад"
		elif lang_data == 'uk':
			text = "Мова успішно змінена на "
			s_back = "Назад"
		else:
			text = "Language successfully changed to "
			s_back = "Back"
		keyboard = [
			[InlineKeyboardButton(f"⬅️ {s_back}", callback_data="settings")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"🇦🇦 {text}*{q3}*", parse_mode='Markdown', reply_markup=buttons)
	if "buycodes_" in query.data:
		qdata = query.data
		qdsplit = qdata.split('_')
		q1 = qdsplit[0]
		q2 = qdsplit[1]
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		lang_data = data[user]["lang"]
		if lang_data == 'ru':
			text = f"Вы уверены что хотите приобрести код на *{q2}*₴?"
			c_yes = "Да"
			c_no = "Нет"
			back = "Профиль"
		elif lang_data == 'uk':
			text = f"Ви впевнені що хочете купити код на *{q2}₴*?"
			c_yes = "Так"
			c_no = "Ні"
			back = "Профіль"
		else:
			text = f"Do you want buy code on *{q2}₴*?"
			c_yes = "Yes"
			c_no = "No"
			back = "Profile"
		keyboard = [
			[InlineKeyboardButton(f"✅ {c_yes}", callback_data=f"yes_buycode_{q2}"),
			InlineKeyboardButton(f"❎ {c_no}", callback_data="profile")],
		]
		buttons = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(f"🌐 {text}", parse_mode='Markdown', reply_markup=buttons)
	if "yes_buycode_" in query.data:
		qdata = query.data
		qdsplit = qdata.split('_')
		q1 = qdsplit[0]
		q2 = qdsplit[1]
		q3 = qdsplit[2]
		try:
			user = context.user_data["user"]
		except:
			user = str(query.from_user.id)
		data = json.loads(open("database.json","r").read())
		shop = json.loads(open("shop.json","r").read())
		lang_data = data[user]["lang"]
		balance = data[user]["balance"]
		if lang_data == 'ru':
			error_money = 'У вас недостаточно средств на балансе'
		elif lang_data == 'uk':
			error_money = 'У вас недостатньо коштів на балансі'
		else:
			error_money = "You don't have enough money"
		if lang_data == 'ru':
			profile = "Профиль"
		elif lang_data == 'uk':
			profile = "Профіль"
		else:
			profile = "Profile"
		if balance < int(q3):
			keyboard = [
				[InlineKeyboardButton(f"👤 {profile}", callback_data="profile")],
			]
			buttons = InlineKeyboardMarkup(keyboard)
			await query.edit_message_text(f"❌ {error_money}", parse_mode='Markdown', reply_markup=buttons)
		else:
			codename = ''
			for i in range(16):
				codename = codename + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
			shop = json.loads(open("shop.json","r").read())
			data[user]["balance"] -= int(q3)
			a = shop["codes"]["code"]
			b = shop["codes"]["value"]
			c = shop["codes"]["amount"]
			d = shop["codes"]["com"]
			a.append(codename)
			b.append(int(q3))
			c.append(1)
			d.append(f"Created by {user}")
			shop["codes"]["code"] = a
			shop["codes"]["value"] = b
			shop["codes"]["amount"] = c
			shop["codes"]["com"] = d
			json.dump(data, open("database.json","w"))
			json.dump(shop, open("shop.json","w"))
			if lang_data == 'ru':
				text = f'Код успешно создан: `{codename}`'
				b = f'Баланс: *{str(data[user]["balance"])}*₴'
			elif lang_data == 'uk':
				text = f'Код успішно створен: `{codename}`'
				b = f'Баланс: *{str(data[user]["balance"])}₴*'
			else:
				text = f'Code successfully created: `{codename}`'
				b = f'Balance: *{str(data[user]["balance"])}₴*'
			await query.edit_message_text(f"☑️ {text}\n💳 {b}", parse_mode='Markdown', reply_markup=buttons)



#permission commands
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		user = update.message.from_user
		chat = update.message.chat
		if user.id in testerID:
			await update.message.reply_text("tesr")
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		user = update.message.from_user
		chat = update.message.chat
		if user.id in adminID:
			text = update.message.text
			r = text.replace('/payment ', '')
			if r == '' or r == ' ' or r == '/payment':
				await update.message.reply_text("❌ Error! Write payment method")
			else:
				data_shop = json.loads(open("shop.json","r").read())
				if r in data_shop["payment"]["list"]:
					l = data_shop["payment"]["list"].index(r)
					if data_shop["payment"]["enabled"][l] == "False":
						data_shop["payment"]["enabled"][l] = "True"
						json.dump(data_shop, open("shop.json","w"))
						await update.message.reply_text(f"❗ *{r}* changed from *False* to *True*", parse_mode='Markdown')
					else:
						data_shop["payment"]["enabled"][l] = "False"
						json.dump(data_shop, open("shop.json","w"))
						await update.message.reply_text(f"❗ *{r}* changed from *True* to *False*", parse_mode='Markdown')
				else:
					await update.message.reply_text(f"❗ *{r}* not found in *shop.json*", parse_mode='Markdown')
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

async def database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		user = update.message.from_user
		chat = update.message.chat
		if user.id in adminID:
			text = "🛠 Choose type of database\n🛍 *Shop* _(1)_\n👥 *User* _(2)_"
			if user.id == ownerID:
				text += "\n🖥 *Config* _(3)_"
			await update.message.reply_text(f"{text}", parse_mode='Markdown')
			return DATABASE_TYPE
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

async def database_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		user = update.message.from_user
		chat = update.message.chat
		message = update.message.text
		if user.id in adminID:
			if message in ["1", "Shop"]:
				text = "🛍 Choose shop data type:\n🍎 *Items* _(1)_\n🌐 *Codes* _(2)_\n_💸 *Payment* _(3)_"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return DATABASE_SHOP
			elif message in ["2", "User", "Users", "Userdata"]:
				text = "👥 Write user ID\n❗ Arguments: `all`"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return DATABASE_USER
			elif message in ["3", "Config", "Configuration"] and user.id == ownerID:
				text = "🖥 Download *config.txt* and send me edited *config.txt*"
				await update.message.reply_document(open("config.txt", 'rb'), caption=f"{text}", parse_mode='Markdown')
				return DATABASE_CONFIG
			else:
				text = "❌ Unkown type: `"+message+"`"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

async def database_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		user = update.message.from_user
		chat = update.message.chat
		message = update.message.text
		if user.id in adminID:
			if message in ["1", "Items", "Item"]:
				text = "🛍 Choose items data:\n🍎 *Item* _(1)_\n🪙 *Price* _(2)_\n💱 *Discount* _(3)_\n🔢 *Amount* _(4)_\n〰️ *Comment*:  _(4)_\n📝 *Purchase tutorial*: _(5)_"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return DATABASE_ITEMS
			elif message in ["2", "Codes", "Code"]:
				text = "🌐 Choose code data:\n🍏 *Code* _(1)_\n🪙 *Value* _(2)_\n🔢 *Amount* _(3)_\n〰️ *Comment*:  _(4)_"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return DATABASE_CODES
			elif message in ["3", "Payment", "Pay"]:
				text = "💸 Choose payment data:\n📔 *List of payments* _(1)_\n✔️ *Toggle* _(2)_"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return DATABASE_PAYMENT
			else:
				text = "❌ Unkown type: `"+message+"`"
				await update.message.reply_text(f"{text}", parse_mode='Markdown')
				return
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

MAILINGTEXT, MAILINGFORWARD = range(2)

async def mailing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		user = update.message.from_user
		chat = update.message.chat
		if user.id in adminID:
			await update.message.reply_text('🏴 *Okay!*\n💬 Now send me text to mail or write `r!forward` for forward mailing', parse_mode='Markdown')
			return MAILINGTEXT
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

async def mailingtext(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
		user = update.message.from_user
		chat = update.message.chat
		if user.id in adminID:
			text = update.message.text
			if text == 'r!forward':
				await update.message.reply_text('🏴 *Good!* Now send me message to forward', parse_mode='Markdown')
				return MAILINGFORWARD
			data = json.loads(open("database.json","r").read())
			try:
				us = 0
				for i in data:
					await context.bot.send_message(chat_id=i, text=text)
					us = i
			except:	
				await update.message.reply_text('❌ *Error!* Message not delivered to `'+str(us)+'`', parse_mode='Markdown')
				data.remove(us)
			await update.message.reply_text('✅ *Done!*\n🗣️ Message sended to', parse_mode='Markdown')
			return ConversationHandler.END
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

async def mailingforward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
		user = update.message.from_user
		chat = update.message.chat
		if user.id in adminID:
			user_data = context.user_data
			type = user_data["mailingtype"]
			text = update.message.text
			data = json.loads(open("database.json","r").read())
			try:
				from_chat = chat.id
				message_id = update.message.id
				us = 0
				for i in data:
					await context.bot.forward_message(chat_id=i, from_chat_id=from_chat, message_id=message_id)
					us = i
			except:
				await update.message.reply_text('❌ *Error!* Message not forwarded to `'+str(us)+'`', parse_mode='Markdown')
			await update.message.reply_text('✅ *Done!*\n🗣️ Message forwarded', parse_mode='Markdown')
			return ConversationHandler.END
		else:
			await update.message.reply_text(f"❌ Access error!\n❗You (`{user.id}`) don't have permission to use this command", parse_mode='Markdown')

CAPTCHA = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	#Send message when "/start" issued
	ef = update.effective_user
	data = json.loads(open("database.json","r").read())
	user = str(update.message.from_user.id)
	if user not in data:
		nickname = update.message.from_user.username
		id = update.message.from_user.id
		lang = update.message.from_user.language_code
		if lang == 'ru':
			text = "Пожалуйста, пройдите проверку с помощью капчи"
		elif lang == 'uk':
			text = "Будь ласка, пройдіть перевірку за допомогою капчи"
		else:
			text = "Please, write captcha"
		try:
			if context.user_data["captcha"] != "":
				context.user_data["captcha"] = "0"
		except:
			context.user_data["captcha"] = "0"
		if context.user_data["captcha"] == "0":
			pattern = ""
			for x in range(random.randrange(6, 12)):
				pattern = pattern + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
			captchaimg = ImageCaptcha(width=random.randrange(200, 400), height=random.randrange(200, 400))
			captchaimg.write(pattern, "captcha.png")
			context.user_data["captcha"] = pattern
			await update.message.reply_photo(open("captcha.png", 'rb'), caption=f"🛡 {text}", parse_mode='Markdown')
			return CAPTCHA
		from datetime import date
		today = date.today()
		today = str(today)
		data[user] = {
			"balance":0,
			"transactions":{
				"item":["Registration"],
				"price":[0],
				"date":[f"{today}"]
			},
			"pubId":[],
			"bans":[],
			"codes":[],
			"lang":lang
		}
		#save
		json.dump(data, open("database.json","w"))
	data = json.loads(open("database.json","r").read())
	balance = data[user]["balance"]
	transaction = data[user]["transactions"]
	lang = data[user]["lang"]
	if lang == 'ru':
		text = f'👋 Привет, {ef.mention_html()}!\n📃 Используй "/profile" чтоб начать покупать!'
	elif lang == 'uk':
		text = f'👋 Привіт, {ef.mention_html()}!\n📃 Використовуй "/profile" щоб почати купувати!'
	else:
		text = f'👋 Hello, {ef.mention_html()}!\n📃 Use "/profile" for start shopping!'
	await update.message.reply_html(text, reply_markup=ForceReply(selective=True, input_field_placeholder="/profile"),
	)

async def captcha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	#Send message when "/start" issued
	lang = update.message.from_user.language_code
	message = update.message.text
	if lang == 'ru':
		correct = "*Верно!* Пожалуйста, используйте */start* снова"
		not_correct = "*Не верно!* Пожалуйста, попробуйте снова"
	elif lang == 'uk':
		correct = "*Вірно!* Будь ласка, використайте */start* знову"
		not_correct = "*Не вірно!* Будь ласка, спробуйте знову"
	else:
		correct = "*Correct!* Please, use */start* again"
		not_correct = "*Not correct!* Please, try again"
	if message.lower() != context.user_data["captcha"].lower():
		pattern = ""
		for x in range(random.randrange(6, 12)):
			pattern = pattern + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
		captchaimg = ImageCaptcha(width=random.randrange(200, 400), height=random.randrange(200, 400))
		captchaimg.write(pattern, "captcha.png")
		context.user_data["captcha"] = pattern
		await update.message.reply_photo(open("captcha.png", 'rb'), caption=f"❌ {not_correct}", parse_mode='Markdown')
		return
	else:
		context.user_data["captcha"] = ""
		await update.message.reply_text(f'✅ {correct}', parse_mode='Markdown')
		return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	if user not in data:
		return
	us = update.message.from_user
	lang = data[user]["lang"]
	if lang == 'ru':
		text = '❔ <b>Помощь</b>\n🏴 Чтоб попасть в профиль используйте <b>кнопку</b> ниже или напишите <b>/profile</b>\n🏴 Если какого либо способа нету - значит его выключили, попробуйте позже\n🏴 Проблемы? Пишите поддержке используя <b>/support</b>\n🏴 Есть код? Активируйте его используя <b>/codes</b>'
		profile = 'Профиль'
	elif lang == 'uk':
		text = '❔ <b>Допомога</b>\n🏴 Щоб попасти у профіль використовуйте <b>кнопку</b> нижче або напишіть <b>/profile</b>\n🏴 Якщо деякого спосіба оплати немає - значить його вимкнули, спробуйте пізніше\n🏴 Проблеми? Пишіть підтримці використовуя <b>/support</b>\n🏴 Є код? Активуйте його використовуя <b>/codes</b>'
		profile = 'Профіль'
	else:
		text = '❔ <b>Help</b>\n🏴 To get in profile, use <b>button</b> below or write <b>/profile</b>\n🏴 If one of payment methods is not found - this method is off, try later\n🏴 Problems? Write to support using <b>/support</b>\n🏴 Do you have code? Activate it using <b>/codes</b>'
		profile = 'Profile'
	keyboard = [
		[InlineKeyboardButton(f"👤 {profile}", callback_data="profile")],
	]
	buttons = InlineKeyboardMarkup(keyboard)
	await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	us = update.message.from_user
	lang = update.message.from_user.language_code
	if user not in data:
		nickname = update.message.from_user.username
		id = update.message.from_user.id
		lang = update.message.from_user.language_code
		if lang not in ['ru', 'uk']:
			lang = 'en'
		from datetime import date
		today = date.today()
		today = str(today)
		data[user] = {
			"balance":0,
			"transactions":{
				"item":["Registration"],
				"price":[0],
				"date":[f"{today}"]
			},
			"pubId":[],
			"bans":[],
			"codes":[],
			"lang":lang
		}
		#save
		json.dump(data, open("database.json","w"))
	data = json.loads(open("database.json","r").read())
	balance = data[user]["balance"]
	transaction = data[user]["transactions"]
	item = transaction["item"]
	price = transaction["price"]
	item = item[len(item)-1]
	price = price[len(price)-1]
	lang = data[user]["lang"]
	if lang == 'ru':
		refill = "Пополнить баланс"
		shop = "Магазин"
		settings = "Настройки"
		text = f'🌀 Твой профиль\n👤 Ник: <b>{us.username}</b>\n🆔 Айди: <b>{us.id}</b>\n💳 Баланс: <b>{balance}</b>₴\n📑 Последняя транзакция: <b>{item}</b> ({price}₴)\n🇷🇺 Язык: <b>{lang}</b>'
	elif lang == 'uk':
		refill = "Поповнити баланс"
		shop = "Магазин"
		settings = "Налаштування"
		text = f'🌀 Твій профіль\n👤 Нік: <b>{us.username}</b>\n🆔 Айді: <b>{us.id}</b>\n💳 Баланс: <b>{balance}</b>₴\n📑 Остання транзакція: <b>{item}</b> ({price}₴)\n🇺🇦 Мова: <b>{lang}</b>'
	else:
		refill = "Refill balance"
		shop = "Shop"
		settings = "Settings"
		text = f'🌀 Your profile\n👤 Nickname: <b>{us.username}</b>\n🆔 ID: <b>{us.id}</b>\n💳 Balance: <b>{balance}</b>₴\n📑 Last transaction: <b>{item}</b> ({price}₴)\n🇺🇸 Language: <b>{lang}</b>'
	profilekeyboard = [
		[InlineKeyboardButton(f"💸 {refill}", callback_data="refillbalance")],
		[InlineKeyboardButton(f"🛍 {shop}", callback_data="shop")],
		[InlineKeyboardButton(f"⚙️ {settings}", callback_data="settings")],
	]
	profilebuttons = InlineKeyboardMarkup(profilekeyboard)
	await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=profilebuttons)

SUPPORTTEXT = range(1)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	if user not in data:
		return
	us = update.message.from_user
	message = update.message.text
	lang = data[user]["lang"]
	bans = data[user]["bans"]
	if lang == 'ru':
		text = "👾 Пожалуйста, опишите вашу проблему как можно детальнее и мы дадим вам ответ при первой возможности\n❗ Отменить команду можно при помощи */cancel*"
		ban = "👾 Простите, но вы заблокированы"
	elif lang == 'uk':
		text = "👾 Будь ласка, опишіть вашу проблему як можна детальніше і ми дамо вам відповідь при першій можливості\n❗ Відминити команду можна за допомогою */cancel*"
		ban = "👾 Вибачте, але ви заблоковані"
	else:
		text = "👾 Please, write your problems with more details and we send feedback when it was can be\n❗ You can cancel command by */cancel*"
		ban = "👾 Sorry, but you are banned"
	if "support" not in bans:
		await update.message.reply_text(text, parse_mode='Markdown')
		return SUPPORTTEXT
	else:
		await update.message.reply_text(ban, parse_mode='Markdown')
		return ConversationHandler.END

async def supporttext(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	us = update.message.from_user
	message = update.message.text
	lang = data[user]["lang"]
	bans = data[user]["bans"]
	if lang == 'ru':
		text = "👾 Спасибо, ваше сообщение было отправлено"
		ban = "👾 Простите, но вы заблокированы"
	elif lang == 'uk':
		text = "👾 Дякую, ваше повідомлення було відправлено"
		ban = "👾 Вибачте, але ви заблоковані"
	else:
		text = "👾 Thanks, your message was delivered"
		ban = "👾 Sorry, but you are banned"
	if "support" not in bans:
		message = f"👾 Message to support from {user}\n🇦🇦 Language: {lang}"
		await context.bot.send_message(ownerID, text=message)
		await context.bot.forward_message(chat_id=ownerID, from_chat_id=update.effective_chat.id, message_id=update.effective_message.id)
		await update.message.reply_text(text, parse_mode='Markdown')
		return ConversationHandler.END
	else:
		await update.message.reply_text(ban, parse_mode='Markdown')
		return ConversationHandler.END

CODESCHOOSE, CODESUSE = range(2)

async def codes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	if user not in data:
		return
	us = update.message.from_user
	message = update.message.text
	lang = data[user]["lang"]
	bans = data[user]["bans"]
	if lang == 'ru':
		text = "🌐 Выберите действие\n🏷 _(1)_ *use* - Используй код\n🪄 _(2)_ *buy* - Купить код\n❗ */cancel* - Отменить команду"
		ban = "🌐 Простите, но вы заблокированы"
	elif lang == 'uk':
		text = "🌐 Оберіть дію\n🏷 _(1)_ *use* - Використати код\n🪄 _(2)_ *buy* - Купити код\n❗ */cancel* - Відмінити команду"
		ban = "🌐 Вибачте, але ви заблоковані"
	else:
		text = "🌐 Choose action\n🏷 _(1)_ *use* - Use code\n🪄 _(2)_ *buy* - By code\n❗ */cancel* - Cancel command"
		ban = "🌐 Sorry, but you are banned"
	if "codes" not in bans:
		await update.message.reply_text(text, parse_mode='Markdown')
		return CODESCHOOSE
	else:
		await update.message.reply_text(ban, parse_mode='Markdown')
		return ConversationHandler.END

async def codeschoose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	
	keyboard = [
	[
		InlineKeyboardButton("25₴", callback_data="buycodes_25"),
		InlineKeyboardButton("50₴", callback_data="buycodes_50")
	],
	[
		InlineKeyboardButton("75₴", callback_data="buycodes_75"),
		InlineKeyboardButton("100₴", callback_data="buycodes_100")
	],
	]
	buttons = InlineKeyboardMarkup(keyboard)
	
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	us = update.message.from_user
	message = update.message.text
	lang = data[user]["lang"]
	bans = data[user]["bans"]
	if lang == 'ru':
		use = "🌐 Напишите код\n❗ */cancel* - Отменить команду"
		buy = "🌐 Выберите стоимость ниже"
		error = f"🌐 Неизвестное действие: *{message}*\n❗ */cancel* - Отменить команду"
		ban = "🌐 Простите, но вы заблокированы"
	elif lang == 'uk':
		use = "🌐 Напишіть код\n❗ */cancel* - Відмінити команду"
		buy = "🌐 Оберіть ціну нижче"
		error = f"🌐 Невідома дія: *{message}*\n❗ */cancel* - Відмінити команду"
		ban = "🌐 Вибачте, але ви заблоковані"
	else:
		use = "🌐 Write code\n❗ */cancel* - Cancel command"
		buy = "🌐 Choose price below"
		error = f"🌐 Unknown action: *{message}*\n❗ */cancel* - Cancel command"
		ban = "🌐 Sorry, but you are banned"
	if "codes" not in bans:
		if message in ["1", "use"]:
			await update.message.reply_text(use, parse_mode='Markdown')
			return CODESUSE
		elif message in ["2", "buy"]:
			await update.message.reply_text(buy, parse_mode='Markdown', reply_markup=buttons)
			return ConversationHandler.END
		else:
			await update.message.reply_text(error, parse_mode='Markdown')
			return
	else:
		await update.message.reply_text(ban, parse_mode='Markdown')
		return ConversationHandler.END

async def codesuse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	shop = json.loads(open("shop.json","r").read())
	us = update.message.from_user
	message = update.message.text
	lang = data[user]["lang"]
	bans = data[user]["bans"]
	if lang == 'ru':
		ban = "🌐 Простите, но вы заблокированы"
	elif lang == 'uk':
		ban = "🌐 Вибачте, але ви заблоковані"
	else:
		ban = "🌐 Sorry, but you are banned"
	if "codes" not in bans:
		Scode = shop["codes"]["code"]
		l = len(Scode)
		err = 0
		for i in range(len(shop["codes"]["code"])):
			Scode = shop["codes"]["code"][i]
			Svalue = shop["codes"]["value"][i]
			Samount = shop["codes"]["amount"][i]
			Scom = shop["codes"]["com"][i]
			if Scode != message:
				err += 1
			else:
				break
		if lang == 'ru':
			successfully = "✅ Код активирован успешно"
			error_not_found = "❌ Код не найден"
			error_max = "❌ Код больше не действителен"
			error_used = "❌ Код уже активирован"
			reward = f"💰 Твоя награда: *{Svalue}₴*"
			ban = "🌐 Простите, но вы заблокированы"
		elif lang == 'uk':
			successfully = "✅ Код активован успішно"
			error_not_found = "❌ Код не найден"
			error_max = "❌ Код більше не дійсний"
			error_used = "❌ Код вже активований"
			reward = f"💰 Твоя нагорода: *{Svalue}₴*"
			ban = "🌐 Вибачте, але ви заблоковані"
		else:
			successfully = "✅ Code activated successfully"
			error_not_found = "❌ Code not found"
			error_max = "❌ Code is expired"
			error_used = "❌ Code already used"
			reward = f"💰 Your reward: *{Svalue}₴*"
			ban = "🌐 Sorry, but you are banned"
		a = data[user]["codes"]
		if err == l:
			await update.message.reply_text(error_not_found, parse_mode='Markdown')
			return
		if message not in shop["codes"]["code"]:
			await update.message.reply_text(error_not_found, parse_mode='Markdown')
			return
		if message in data[user]["codes"]:
			await update.message.reply_text(error_used, parse_mode='Markdown')
			return
		if Samount == 0:
			await update.message.reply_text(error_max, parse_mode='Markdown')
			return
		if Scode in a:
			await update.message.reply_text(error_used, parse_mode='Markdown')
			return
		a = data[user]["codes"]
		a.append(Scode)
		data[user]["balance"] += Svalue
		data[user]["codes"] = a
		if Samount != -1:
			l = shop["codes"]["code"].index(Scode)
			shop["codes"]["amount"][l] -= 1
		json.dump(data, open("database.json","w"))
		json.dump(shop, open("shop.json","w"))
		await update.message.reply_text(f"{successfully}\n{reward}\n_{Scom}_", parse_mode='Markdown')
		return ConversationHandler.END
	else:
		await update.message.reply_text(ban, parse_mode='Markdown')
		return ConversationHandler.END

async def codesbuy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = str(update.message.from_user.id)
	context.user_data["user"] = user
	data = json.loads(open("database.json","r").read())
	shop = json.loads(open("shop.json","r").read())
	us = update.message.from_user
	message = update.message.text
	lang = data[user]["lang"]
	bans = data[user]["bans"]
	if lang == 'ru':
		text = "🌐 Выберите стоимость ниже"
		ban = "🌐 Простите, но вы заблокированы"
	elif lang == 'uk':
		text = "🌐 Оберіть ціну нижче"
		ban = "🌐 Вибачте, але ви заблоковані"
	else:
		text = "🌐 Choose price below"
		ban = "🌐 Sorry, but you are banned"
	if "codes" not in bans:
		keyboard = [
		[
			[InlineKeyboardButton(f"25₴", callback_data="buycodes_25")],
			[InlineKeyboardButton(f"50₴", callback_data="buycodes_50")],
			[InlineKeyboardButton(f"75₴", callback_data="buycodes_75")],
			[InlineKeyboardButton(f"100₴", callback_data="buycodes_100")],
		],
		[
			[InlineKeyboardButton(f"250₴", callback_data="buycodes_250")],
			[InlineKeyboardButton(f"500₴", callback_data="buycodes_500")],
			[InlineKeyboardButton(f"750₴", callback_data="buycodes_750")],
			[InlineKeyboardButton(f"1000₴", callback_data="buycodes_1000")],
		]
	]
		buttons = InlineKeyboardMarkup(keyboard)
		await update.message.reply_text(text, parse_mode='Markdown', reply_markup=buttons)
		return ConversationHandler.END
	else:
		await update.message.reply_text(ban, parse_mode='Markdown')
		return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id-1)
	await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id)
	return ConversationHandler.END

#async def userecho(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#	#Echo users message
#	await update.message.reply_text(update.message.text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
	#Log the error and send a telegram message to notify the developer.
	#Log the error before we do anything else, so we can see it even if something breaks.
	logger.error(msg="Exception while handling an update:", exc_info=context.error)

	#Traceback.format_exception returns the usual python message about an exception, but as a list of strings rather than a single string, so we have to join them together.
	tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
	tb_string = "".join(tb_list)

	#Build the message with some markup and additional information about what happened.
	#You might need to add some logic to deal with messages longer than the 4096 character limit.
	update_str = update.to_dict() if isinstance(update, Update) else str(update)
	message = (
		f"PTB: {TG_VER} | BOT: {version}"
		f"\nAn exception was raised while handling an update\n"
		f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
		"</pre>\n\n"
		f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
		f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
		f"<pre>{html.escape(tb_string)}</pre>"
	)

	#Finally, send the message
	#user = update.effective_message.user_id
	await update.message.reply_text(
		text='❗Error log sended to owner!', parse_mode=ParseMode.HTML
	)
	await context.bot.send_message(
		chat_id=ownerID, text=message, parse_mode=ParseMode.HTML
	)

def main() -> None:
	#Start bot
	#Create the Application and pass it your bot's token.
	application = Application.builder().token(TelegramBotToken).build()

	#On different commands - answer in Telegram
	if onUpdate == False:
		#query
		application.add_handler(CallbackQueryHandler(querybuttons))
		mailingconv = ConversationHandler(
			entry_points=[CommandHandler("mailing", mailing)],
			states={
				MAILINGTEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, mailingtext)],
				MAILINGFORWARD: [MessageHandler(filters.ALL, mailingforward)],
			},
			fallbacks=[CommandHandler("cancel", cancel)],
		)
		application.add_handler(mailingconv)
		#permissions
		application.add_handler(CommandHandler("test", test))
		application.add_handler(CommandHandler("payment", payment))
		#default
		#application.add_handler(CommandHandler("start", start))
		startconv = ConversationHandler(
			entry_points=[CommandHandler("start", start)],
			states={
				CAPTCHA: [MessageHandler(filters.ALL, captcha)],
			},
			fallbacks=[CommandHandler("start", start)],
		)
		application.add_handler(startconv)
		application.add_handler(CommandHandler("help", help))
		application.add_handler(CommandHandler(["profile", "account"], profile))
		supportconv = ConversationHandler(
			entry_points=[CommandHandler("support", support)],
			states={
				SUPPORTTEXT: [MessageHandler(filters.ALL & ~filters.COMMAND, supporttext)],
			},
			fallbacks=[CommandHandler("cancel", cancel)],
		)
		application.add_handler(supportconv)
		codesconv = ConversationHandler(
			entry_points=[CommandHandler(["codes", "code"], codes)],
			states={
				CODESCHOOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, codeschoose)],
				CODESUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, codesuse)],
			},
			fallbacks=[CommandHandler("cancel", cancel)],
		)
		application.add_handler(codesconv)
	else:
		application.add_handler(MessageHandler(filters.COMMAND, onUpdate))

	application.add_error_handler(error_handler)

	#On non command i.e message - echo the message on Telegram
#	application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, userecho))

	#Run the bot until the user presses Ctrl-C
	application.run_polling()


if __name__ == "__main__":
	main()