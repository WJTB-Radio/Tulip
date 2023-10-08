import discord
from datetime import *
from pytz import timezone
from discord.ext import commands
import sqlite3 as sqlite
from discord import app_commands
import sys
import os
import subprocess
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
		channel = client.get_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		if(not is_admin(user)):
			return
		if(isinstance(channel, discord.TextChannel)):
			if(not check_channel(channel)):
				# dont care about other channels
				return
		else:
			# only care about normal text channels
			return
		if(not type(emoji) is str):
			# we dont care about custom emojis
			return
		if(emoji == '✅'):
			add_message_to_gallery(message, message.created_at, '')
		elif(emoji == '❌'):
			remove_message_from_gallery(message)

	@client.event
	async def on_message(message):
		if(not is_admin(message.author)):
			return
		if(message.reference is None):
			# this isnt a reply
			return
		channel = message.channel
		content = message.content.lstrip()+"\n\n"
		if(not check_channel(channel)):
			return
		if(not content.startswith('✅')):
			return
		image_message = await channel.fetch_message(message.reference.message_id)
		m = re.search('(?i)date: *(.*)\\n', content)
		date = image_message.created_at
		if(not m is None):
			datestring = m.group(1)
			try:
				date = datetime.strptime(datestring, '%m/%d/%Y')
			except ValueError:
				await message.reply(f'Invalid date \'{datestring}\'\n date must be in mm/dd/yyyy format.')
				return
		m = re.search('(?i)caption: *(.*)\\n', content)
		caption = ''
		if(not m is None):
			caption = m.group(1)
		add_message_to_gallery(image_message, date, caption)

def add_message_to_gallery(message, timestamp, caption):
	attachments = message.attachments
	for attachment in attachments:
		if(not attachment.content_type.startswith('image')):
			# dont care about attachements that arent images
			continue
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
	url = convert_image(url)
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = cur.execute("SELECT * FROM gallery WHERE image = ?", (url,)).fetchone()
	if(not result is None):
		# this image is already in the gallery
		con.close()
		return
	result = cur.execute("INSERT INTO gallery(image, date_taken, caption) VALUES(?, ?, ?)", (url, timestamp, caption)).fetchone()
	con.commit()
	con.close()
	output.update()

def remove_image_from_gallery(url):
	# we use the hash of the resized image as the filename so this should be fine
	url = convert_url(url)
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	cur.execute("DELETE FROM gallery WHERE image = ?", (url,))
	con.commit()
	con.close()
	output.update()

def convert_image(url):
	# discord doesnt work as a cdn anymore so we have to use github instead
	subprocess_result = subprocess.run(["/var/services/homes/admin/tulip/resize.sh", url], capture_output=True)
	url = subprocess_result.stdout.strip()
	if(url == ""):
		# something went wrong, aka this image is invalid
		return
	url = "https://raw.githubusercontent.com/WJTB-Radio/ShowData/master/images/" + url
	return url

def check_channel(channel):
	return channel.name in ['website-gallery', 'pics-and-vids', 'botchat']

def is_admin(user):
	if(not isinstance(user, discord.Member)):
		return False
	for role in user.roles:
		if(role.name == "tulip-admin"):
			return True
	return False
