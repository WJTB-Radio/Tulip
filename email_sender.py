import asyncio
import discord
from datetime import *
import re

import live_events_email
import live_events_calendar
import output

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
```
Example Acceptance Usage:
```
✅
name: Ian Henry Atkins
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
		if(channel.name != "upcoming-events"):
			return
		content = message.content.lstrip()+"\n\n"
		accepted = content.startswith('✅')
		rejected = content.startswith('❌')
		calendaronly = content.startswith('📅') or content.startswith('🗓️') or content.startswith('📆')
		if(not (accepted or rejected or calendaronly)):
			return
		referenced_message = await channel.fetch_message(message.reference.message_id)
		if(len(referenced_message.embeds) <= 0):
			return
		embed_content = referenced_message.embeds[0].description

		date = None
		m = re.search(r'(?i) ?\*\* ?What is the date of the event ?\? ?\*\* ?\n ?([0-9]*-[0-9]*-[0-9]*) ?', embed_content, re.M)
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

		m = re.search(r'(?i) ?\*\* ?What is the name of the event ?\? ?\*\* ?\n ?(.*) ?\n', embed_content, re.M)
		if(m is None):
			await message.reply('Could not find name of event in referenced message.')
			return
		event_name = m.group(1)

		m = re.search(r' ?A new live event has been submitted. ?\n ?Someone with the following email (.*@.*) responded to the survey', referenced_message.content, re.M)
		if(m is None):
			await message.reply("Email not found in referenced message.")
			return
		email = m.group(1)

		name = ""
		if(not calendaronly):
			m = re.search('(?i)name: *(.*)', content)
			if(m is None):
				await message.reply(f"You must specify the name of the person this email is directed towards.\n{example_usage}")
				return
			name = m.group(1)

		reason = None
		if(rejected):
			m = re.search('(?i)reason: *(.*)', content)
			if(m is None):
				await message.reply(f"You must specify a reason\n{example_usage}")
				return
			reason = m.group(1)
		if(accepted):
			calendar_error = live_events_calendar.add_calendar_event(embed_content)
			if(calendar_error is not None):
				await message.reply(f"❌ Error: \n{calendar_error}")
		elif(calendaronly):
			calendar_error = live_events_calendar.add_calendar_event(embed_content)
			if(calendar_error is not None):
				await message.reply(f"❌ Error: \n{calendar_error}")
			else:
				await message.reply(
					f"This event has been added to the live events calendar. It may take a few minutes for the update to propagate."
				)
				output.update()
				await asyncio.sleep(5)
				output.push()
			return
		sent_message = live_events_email.send_live_events_email(name, email, event_name, date, reason)
		await message.reply(
			f"Email sent ✅\n```{sent_message}```\n"+
			(f"This event has been added to the live events calendar. It may take a few minutes for the update to propagate." if accepted else ""))
		output.update()
		await asyncio.sleep(5)
		output.push()