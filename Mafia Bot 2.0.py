# Стандартные Python-библиотеки
import asyncio	# Модуль для ассинхронного ввода/вывода
import sqlite3	# Модуль для работы с базами данных 
from random import choice	# Для выбора рандомного элемента списка

from datetime import datetime # Модуль для вывода даты

# Библиотека для создания Discord-бота
import discord
from discord.ext import commands

# ↓ Модуль для создания страниц по реакциям в embed
from Cybernator import Paginator as pag

# Конфигурации бота
from config import settings


# Создаем переменную для управления ботом и 'устанавливаем' префикс
bot = commands.Bot( command_prefix = settings['PREFIX'])
bot.remove_command('help')	# Удаляем команду help

presenterID = 697988271405269073	# ID роли ведущего


def globaliz():
	'''Функция, которая делает переменные глобальными'''
	global maf_channel

	# ↓ Канал, где играют в мафию:
	maf_channel = bot.get_channel(729550452856848435)


def AddTime():
	'''Функция для обновления значеный 
	переменных даты и времени
	'''
	global today
	global vrem

	minu = 0

	today = datetime.now().date()	# Дата
	tm = datetime.now()
	vrem = "{}:{}".format(tm.hour, tm.minute)	# Время

	if tm.minute < 10:
		minu = f"0{tm.minute}"
	else:
		minu = tm.minute

	vrem = "{}:{}".format(tm.hour, minu)	# Время

# Создаем базу данных
DataBase = sqlite3.connect('Zefur_Users.db')

# Объект cursor позволяет работать с базой: добовлять/удалять
# изменять/использовать данные базы
cursor = DataBase.cursor()  


@bot.event
async def on_ready():
	'''Стартовая функция'''
	print('Бот запущен!')

	# Создаем таблицу и добавляем столбцы
	# (таблица не будет создаваться заново, если она уже существует)
	cursor.execute(
			"""
				CREATE TABLE IF NOT EXISTS users(
					memb TEXT,
					ment TEXT,
					id BIGINT,
					points BIGINT,
					server_id BIGINT
				)
			"""
		)
	# memb - member
	# ment - mention юзера
	# id - id юзера
	# points - кол-во очков юзера

	DataBase.commit()	#  Подтверждаем создание таблицы
	print('Таблица создана!')

	for guild in bot.guilds:
		for member in guild.members:
			temporary_variable = cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone()
			
			if temporary_variable is None:
				# Заносим данные в таблицу
				cursor.execute(
						f"INSERT INTO users VALUES('{member}','{member.mention}', '{member.id}', '{0}', {guild.id})"
					)
			else:
				pass

	DataBase.commit()	# Сохраняем изменения

	print('Данные внесены в таблицу!')
	print('SUCCES')


@bot.event
async def on_member_join(member):
	'''Функция, которая активируется тогда, 
	когда к серверу присоединился новый участник
	'''
	temporary_variable = cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone()
	
	# Заносим данные о новом игроке в таблицу
	if temporary_variable is None:
		# Заносим данные в таблицу
		cursor.execute(
				f"INSERT INTO users VALUES('{member}','{member.mention}', '{member.id}', '{0}', {member.guild.id})"
			)
		DataBase.commit()	# Сохраняем изменения
	else:
		pass


@bot.command()
async def users(ctx):
	'''Команда для вывода кол-ва участников сервера'''
	await ctx.message.delete()
	await asyncio.sleep(0.5)

	AddTime()

	colors = [
		0xff8c00, 0x4B0082, 0x808080, 
		discord.Color.green(),
		discord.Color.blue()
	]

	guild = bot.get_guild(655544918923542528)
	emb = discord.Embed(
			title = 'Количество участников сервера {}: {} '.format(
					ctx.author.guild.name, len(guild.members)
				),
			color = choice(colors)
		)
	emb.set_author(
			name = '{}, {}'.format(today, vrem),
			icon_url = bot.user.avatar_url
		)
	await ctx.channel.send(embed=emb)



# Этой командой могут пользоваться только участники с ролью 
# "Ведущий"
@bot.command(aliases=['победил'])
@commands.has_role(presenterID)	
async def winner(ctx, member:discord.Member=None):
	globaliz()

	if ctx.channel.id == 729550452856848435:
		'''Функция начисления очков победителю'''
		amount = 5

		# ↓ Если ведущий не указал конкретного игрока
		if member is None:
			await ctx.channel.send(
					f"{ctx.author.mention}, **укажите человека, которого вы хотите вознаградить!**"
				)
			await ctx.message.add_reaction('\U0000274c')
			await asyncio.sleep(1)

		else:
			# ↓ если ведущий хочет начислить очки самому себе
			if member.mention == ctx.author.mention:
				await ctx.message.add_reaction('\U0000274c')
				await asyncio.sleep(1)

				await ctx.channel.send("{}, **нельзя начислять очки самому себе!** ".format(ctx.author.mention))
			
			else:
				await ctx.message.add_reaction('\u2705')
				await asyncio.sleep(1)

				# ↓ Обновляем баланс победителя
				cursor.execute(
						"UPDATE users SET points = points + {} WHERE id = {}".format(amount, member.id)
					)

				# Подтверждаем изменения и заносим их в базу данных
				DataBase.commit()


				emb =  discord.Embed(
						description = f"**Игрок {member.mention} победил и получил {amount} очков!** :fire: ",
						color = discord.Color.green()
					)
				await ctx.channel.send(embed=emb)

		await ctx.message.delete() # Удаляем сообщение с командой

	else:
		await ctx.send(
				f"**{ctx.author.mention}, использовать эту команду можно только в канале, где играют в мафию({maf_channel.mention})**:rage:"
			)



@bot.command(aliases=['отнять'])
@commands.has_role(presenterID)	
async def take(ctx, member:discord.Member=None, amount=None):
	'''Функция отнятия очков у игрока'''
	globaliz()

	if ctx.channel.id == 729550452856848435:
		# ↓ Если ведущий не указал конкретного игрока
		if member is None:
			await ctx.message.add_reaction('\U0000274c')
			await asyncio.sleep(1)	
			await ctx.message.delete()

			await ctx.channel.send(
					f"{ctx.author.mention}, **укажите человека, у которого вы хотите отнять очки!**"
				)


		# ↓ Если ведущий указал себя в качестве member
		elif member.mention == ctx.author.mention:
			await ctx.message.add_reaction('\U0000274c')
			await asyncio.sleep(1)	
			await ctx.message.delete()

			await ctx.channel.send(f"{ctx.author.mention}, **вы не можете отнимать очки у самого себя!**")	

		# Прочие случаи:
		else:
			if amount is None:
				# 1: Если ведущий не указал никакой суммы:
				# В этом случае игрок потеряет 5 очков.

				# ↓ Снимаем 5 очков со счета юзера
				amount = 5
				cursor.execute(
						"UPDATE users SET points = points - {} WHERE id = {}".format(amount, member.id)
					)

				await ctx.message.add_reaction('\u2705')
				await asyncio.sleep(1)	
				await ctx.message.delete()

				emb = discord.Embed(
						description = f'**Игрок {member.mention} потерял {amount} очков :(**',
						color = discord.Color.red()
					)	

				await ctx.channel.send(embed=emb)	

			
			else:
				# Во всех других случаях  amount не божет быть None,
				# поэтому я поместил их в else

				amount = amount.lower().strip()

				if amount == 'all':
					# 2: Если ведущий указал all в качестве amount:
					# В этом случае игрок потеряет все свои очки

					cursor.execute(
							"UPDATE users SET points = {} WHERE id = {}".format(0, member.id)
						)

					await ctx.message.add_reaction('\u2705')
					await asyncio.sleep(1)	
					await ctx.message.delete()

					emb = discord.Embed(
							description = f'**Игрок {member.mention} потерял все свои очки!**:cry:',
							color = discord.Color.red()
						)	

					await ctx.channel.send(embed=emb)

				else:
					# 3: Если ведущий указал что-то другое в качестве amount:

					# Скорее всего, amount - это цифра. 
					# Если это так, то бот будет вычетать amount из общего кол-ва очков данного игрока.

					cursor.execute(
							"UPDATE users SET points = points - {} WHERE id = {}".format(
								int(amount), member.id
								)
						)

					await ctx.message.add_reaction('\u2705')
					await asyncio.sleep(1)	
					await ctx.message.delete()

					emb = discord.Embed(
							description = f'**Игрок {member.mention} потерял {amount} очков :(**',
							color = discord.Color.red()
						)	

					await ctx.channel.send(embed=emb)
	else:
		await ctx.send(
			f"**{ctx.author.mention}, использовать эту команду можно только в канале, где играют в мафию({maf_channel.mention})**:rage:"
		)		


@bot.command(aliases=['баланс'])
async def user_info(ctx, member:discord.Member=None):
	'''Функция вывода информации о участнике '''
	globaliz()

	if ctx.channel.id == 729550452856848435:
		await ctx.message.delete()
		await asyncio.sleep(0.5)

		# Если юзер ничего не указывал к команде, то будет 
		# выводится информация о нем самом
		if member is None:	
			# ↓ Следующей строкой мы обращаемся к базе данных
			# и достаем из нее кол-во очком юзера с определенным id
			# (юзера, который отправил сообщение).
			self_point = cursor.execute(
					"SELECT points FROM users WHERE id = {}".format(ctx.author.id)
				).fetchone()[0]
			# => self_point - кол-во очков юзера

			
			emb = discord.Embed(
					description=f"""Очки игрока **{ctx.author.mention}**:  **{self_point}**:gem:"""
				)
		else:
			# Если пользователь хочет узнать инфу о другом пользователе:
			user_point = cursor.execute(
					"SELECT points FROM users WHERE id = {}".format(member.id)
				).fetchone()[0]
			# => user_point - кол-во очков юзера

			
			emb = discord.Embed(
					description=f"""Очки игрока **{member.mention}**:  **{user_point}**:gem:"""
				)
		await ctx.channel.send(embed=emb)

	else:
		await ctx.send(
			f"**{ctx.author.mention}, использовать эту команду можно только в канале, где играют в мафию({maf_channel.mention})**:rage:"
		)	


@bot.command(aliases=['топ'])
async def lb(ctx):
	'''Функция вывода топ-листа сервера'''
	# ↓ emb1 и emb2 - наши страницы топ-листа
	emb1 = discord.Embed(title='Топ 10 игроков:', color=0xFFD700)
	emb2 = discord.Embed(color=0xFFD700)

	counter = 0
	top_data = cursor.execute(
			"SELECT memb, points FROM users WHERE server_id = {} ORDER BY points DESC LIMIT 10".format(
				ctx.guild.id
				)
		)

	for col in top_data:
		counter += 1
		if counter == 1:
			top_cup = '🏆'	# Кубок выводится рядом с именем лидера игры
		else:
			top_cup = ''

		if counter <= 5:
			emb1.add_field(
					name = f"#{counter} | @{col[0]} {top_cup}",
					value = f"Баланс: {col[1]}:gem:",
					inline = False
				)
		else:
			emb2.add_field(
					name = f"#{counter} | @{col[0]} {top_cup}",
					value = f"Баланс: {col[1]}:gem:",
					inline = False
				)

	embeds = [emb1, emb2]	# Список страниц

	msg = await ctx.send(embed=emb1)
	page = pag(
			bot, msg, only=None, use_more=False, embeds=embeds,
			timeout=60
		)
	await page.start()

@bot.command()
async def cls(ctx, *, amount=100):
	await ctx.channel.purge(limit=amount)


async def best_player():
	'''Функция нахождения лучшего игрока и выдачи ему 
	соответствующей роли.
	'''
	# Потом допишу код, сейчас мне надо пиздовать на дачу
	# я ебал её в рот

# tasks - список асинхронных функций
tasks = [
	asyncio.ensure_future(best_player())
]

# Создаем цикл событий 
event_loop = asyncio.get_event_loop()

event_loop.run_until_complete(asyncio.gather(*tasks))


# Подключение бота
bot.run(settings['TOKEN'])