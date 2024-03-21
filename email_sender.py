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
import live_events_email

def is_email_sender(user):
	if(not isinstance(user, discord.Member)):
		return False
	for role in user.roles:
		if(role.name == "live-events-email-sender"):
			return True
	return False

example_usage = """\
Example Rejection Usage:
```
❌
reason: staff availability
name: Ian Henry Atkins
email: iha4@njit.edu, anotheremail@njit.edu
```
Example Acceptance Usage:
```
✅
name: Ian Henry Atkins
email: iha4@njit.edu, optional\
```
"""

def add_module(client):
	@client.event
	async def on_message(message):
		if(not is_email_sender(message.author)):
			return
		if(message.reference is None):
			# this isnt a reply
			return
		channel = message.channel
		content = message.content.lstrip()+"\n\n"
		if(channel.name != "upcoming-events"):
			return
		accepted = content.startswith('✅')
		rejected = content.startswith('❌')
		if(not (accepted or rejected)):
			return
		referenced_message = await channel.fetch_message(message.reference.message_id)
		if(len(referenced_message.embeds) <= 0):
			return
		embed_content = referenced_message.embeds[0].description

		date = None
		m = re.search('(?i)\*\*What is the date of the event\?\*\*\\\n([0-9]+-[0-9]+-[0-9]+)\\n', embed_content, flag=re.MULTILINE)
		if(not m is None):
			datestring = m.group(1)
			try:
				date = datetime.strptime(datestring, '%Y-%m-%d')
			except ValueError:
				await message.reply(f'Invalid date \'{datestring}\'\n date must be in yyyy-mm-dd format.')
				return
		else:
			await message.reply('Could not find date in referenced message.')
			return

		m = re.search('(?i)\*\*What is the name of the event\\?\*\*\\n([0-9]+-[0-9]+-[0-9]+)\\n', embed_content, flag=re.MULTILINE)
		if(m is None):
			await message.reply('Could not find name of event in referenced message.')
			return
		event_name = m.group(1)

		m = re.search("""A new live event has been submitted.\\n Someone with the following email (.*@.*) responded to the survey\\n""", referenced_message.content, flag=re.MULTILINE)
		if(m is None):
			await message.reply("Email not found in referenced message.")
			return
		email = m.group(1)

		m = re.search('(?i)name: *(.*)', content)
		if(m is None):
			await message.reply(f"You must specify a name.\n{example_usage}")
			return
		name = m.group(1)

		reason = None
		if(rejected):
			m = re.search('(?i)reason: *(.*)', content)
			if(m is None):
				await message.reply(f"You must specify a reason\n{example_usage}")
				return
			reason = m.group(1)

		sent_message = send_live_events_email(name, email, event_name, accepted, reason)
		await message.reply(f"Email sent ✅\n```{sent_message}```")

