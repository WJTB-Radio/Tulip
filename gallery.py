import discord
from datetime import *
from pytz import timezone
from discord.ext import commands
import sqlite3 as sqlite
from discord import app_commands
import sys
import os
from threading import Timer
import asyncio
import re

import util
import output

def add_module(client):
	@client.event
	async def on_raw_reaction_add(payload):
		emoji = payload.emoji.name
		user = payload.member
		channel = await client.get_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		print("got reaction")
		if(not is_admin(user)):
			print("reaction by non admin")
			return
		if(isinstance(reaction.message.channel, discord.TextChannel)):
			if(not check_channel(channel)):
				# dont care about other channels
				print("wrong channel")
				return
		else:
			# only care about normal text channels
			print("not a normal text channel")
			return
		if(not type(emoji) is str):
			# we dont care about custom emojis
			print("custom emoji")
			return
		if(emoji == '✅'):
			print("check reaction")
			add_message_to_gallery(message, message.created_at, '')
		elif(emoji == '❌'):
			print("x reaction")
			remove_message_from_gallery(message)
		else:
			print("other emoji:")
			print(emoji)

	@client.event
	async def on_message(message):
		if(not is_admin(message.author)):
			print("not admin")
			return
		if(message.reference is None):
			# this isnt a reply
			print("non reply")
			return
		channel = message.channel
		if(not check_channel(channel)):
			print("wrong channel")
			return
		if(not message.content.startswith('✅')):
			print("not a check")
			return
		image_message = await channel.fetch_message(message.reference.message_id)
		print("got image message")
		m = re.search('(?i)date: *(.*)\\n', message.content)
		date = image_message.created_at
		if(not m is None):
			datestring = m.group(1)
			try:
				date = datetime.strptime(datestring, '%m/%d/%Y')
			except ValueError:
				await message.reply(f'Invalid date \'{datestring}\'\n date must be in mm/dd/yyyy format.')
				return
		m = re.search('(?i)caption: *(.*)\\n', message.content)
		caption = ''
		if(not m is None):
			caption = m.group(1)
		print("adding message to gallery")
		add_message_to_gallery(image_message, date, caption)

def add_message_to_gallery(message, timestamp, caption):
	attachments = message.attachments
	for attachment in attachments:
		print("attachment")
		if(not attachment.content_type.startswith('image')):
			# dont care about attachements that arent images
			continue
		print("image attachment")
		url = str(attachment)
		add_image_to_gallery(url, timestamp, caption)

def remove_message_from_gallery(message):
	attachments = message.attachments
	for attachment in attachments:
		if(not attachment.content_type.startswith('image')):
			# dont care about attachements that arent images
			continue
		url = str(attachment)
		remove_image_from_gallery(url)

def add_image_to_gallery(url, timestamp, caption):
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = cur.execute("SELECT * FROM gallery WHERE image = ?", (url,)).fetchone()
	if(not result is None):
		# this image is already in the gallery
		con.close()
		return
	result = cur.execute("INSERT INTO gallery(image, date_taken, caption)", (url, timestamp, caption)).fetchone()
	con.commit()
	con.close()
	output.update()

def remove_image_from_gallery(url):
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	cur.execute("DELETE FROM gallery WHERE image = ?", (url,))
	con.close()
	output.update()

def check_channel(channel):
	return channel.name in ['gallery', 'pics-and-vids', 'botchat']

def is_admin(user):
	if(not isinstance(user, discord.Member)):
		return False
	for role in user.roles:
		if(role.name == "tulip-admin"):
			return True
	return False
