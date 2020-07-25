# Стандартные Python-библиотеки
import asyncio	# Модуль для ассинхронного ввода/вывода
import sqlite3	# Модуль для работы с базами данных 
from random import choice	# Для выбора рандомного элемента списка

from datetime import datetime # Модуль для вывода даты

# Библиотека для создания wDiscord-бота
import discord
from discord.ext import commands

# ↓ Модуль для создания страниц по реакциям в embed
from Cybernator import Paginator as pag

# Конфигурации бота
import config


bot = commands.Bot( command_prefix = config.settings['PREFIX'])
bot.remove_command('help')	

presenterID = 697988271405269073	# ID роли ведущего


# Подключение бота
bot.run(config.settings['TOKEN'])