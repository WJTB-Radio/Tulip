#!/afs/cad/linux/anaconda3.9.13/anaconda/bin/python3.9

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3 as sqlite
from datetime import *
from pytz import timezone
import sys

if(len(sys.argv) != 2):
	print("please supply a path to the sqlite3 database as a commandline argument")
	sys.exit()

DB_PATH = sys.argv[1]
GUILD_ID = 172047876384358400

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday"] 

@tree.command(name="notdoingmyshow", description="Run this command to announce that you aren't doing your show this week.", guild=discord.Object(id=GUILD_ID))
async def notdoingmyshow(context, day:str=""):
	await set_is_running(context, day, 0)

@tree.command(name="doingmyshow", description="Run this command to announce that you are doing your show this week.", guild=discord.Object(id=GUILD_ID))
async def doingmyshow(context, day:str=""):
	await set_is_running(context, day, 1)

def get_timestamp(time_seconds, w, end_time_seconds=None):
	if(end_time_seconds is None):
		end_time_seconds = time_seconds
	cur_dt = datetime.now(timezone("US/Eastern"))
	cur_w = cur_dt.weekday()
	if(w < cur_w):
		w += 7
	cur_time_seconds = cur_dt.second+cur_dt.minute*60+cur_dt.hour*60*60
	if(w == cur_w and cur_time_seconds > end_time_seconds):
		w += 7
	cur_date = cur_dt.date()
	d = cur_date + timedelta(days=w-cur_w)
	t = time(hour=int(time_seconds/(60*60)), minute=int((time_seconds/60)%60))
	dt = datetime.combine(d, t)
	timestamp = dt.timestamp()
	return int(timestamp)

def format_show(name, hosts, desc, day, start_time, end_time, is_running):
	w = days_of_week.index(day)
	time = f"<t:{get_timestamp(start_time, w, end_time)}:t>-<t:{get_timestamp(end_time, w)}:t>"
	running = "" if is_running == 1 else "**The next show has been cancelled.**"
	return f"**{name}**\n{time}\n{day}\n**hosted by**\n{hosts}\n**description**\n{desc}\n\n{running}"

@tree.command(name="displayshow", description="Display some details about a specific show.", guild=discord.Object(id=GUILD_ID))
async def displayshow(context, name:str):
	con = sqlite.connect(DB_PATH)
	cur = con.cursor()
	message = f"Error: show \"{name}\" not found."
	for day in days_of_week:
		result = cur.execute(f"SELECT name, hosts, desc, start_time, end_time, is_running FROM {day} WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
		if(not result is None):
			message = format_show(result[0], result[1], result[2], day, result[3], result[4], result[5])
			break
	con.close()
	await context.response.send_message(message)

@tree.command(name="nowplaying", description="Check the currently playing show.", guild=discord.Object(id=GUILD_ID))
async def nowplaying(context):
	message = ""
	dt = datetime.now(timezone("US/Eastern"))
	w = dt.weekday()
	if(w >= 5):
		message = "Nothing is playing right now."
	else:
		day = days_of_week[w]
		time = dt.second+dt.minute*60+dt.hour*60*60
		con = sqlite.connect(DB_PATH)
		cur = con.cursor()
		result = cur.execute(f"SELECT name, hosts, desc, start_time, end_time, is_running FROM {day} WHERE start_time < ? AND end_time > ? AND is_running = 1", (time, time)).fetchone()
		if(result is None):
			message = "Nothing is playing right now."
		else:
			message = format_show(result[0], result[1], result[2], day, result[3], result[4], result[5])
		con.close()
	await context.response.send_message(message)

def parse_time(s):
	split = s.strip().lower().split(":")
	hour = 0
	minute = 0
	try:
		if(len(split) == 2):
			if(len(split[0]) not in [1, 2]):
				return None
			hour = int(split[0])
			if(split[1].endswith("pm")):
				split[1] = split[1][:-2].strip()
				if(hour != 12):
					hour += 12
			elif(split[1].endswith("am")):
				if(hour > 12):
					return None
				if(hour == 12):
					hour = 0
				split[1] = split[1][:-2].strip()
			if(len(split[1]) != 2):
				return None
			minute = int(split[1])
		elif(len(split) == 1):
			offset = 0
			if(split[0].endswith("am")):
				split[0] = split[0][:-2].strip()
				if(int(split[0]) == 12):
					offset = -12 # why is 12 hour time like this
				if(int(split[0]) > 12):
					return None
			elif(split[0].endswith("pm")):
				offset = 12
				split[0] = split[0][:-2].strip()
				if(int(split[0]) == 12):
					offset = 0 # why is 12 hour time like this
			if(len(split[0]) in [1, 2]):
				hour = int(split[0])+offset
			else:
				return None
		else:
			return None
	except ValueError:
		return None
	except IndexError:
		return None
	if(hour >= 24 or minute >= 60):
		return None
	return hour*60*60+minute*60

async def check_admin(context):
	for role in context.user.roles:
		if(role.name == "tulip-admin"):
			return True
	await context.response.send_message("You do not have permission to do that.")
	return False

@tree.command(name="addshow", description="Add a show.", guild=discord.Object(id=GUILD_ID))
async def addshow(context, name:str, hosts:str, host_discords:str, desc:str, poster:str, day:str, start_time:str, end_time:str):
	if(not await check_admin(context)):
		return
	host_discords = " "+host_discords.strip()+" "
	day = day.lower()
	message = ""
	if(not day in days_of_week):
		message = f"\"{day}\" is not a valid day of the week.\nThe valid days of the week are monday, tuesday, wednesday, thursday, and friday."
	else:
		start_time_int = parse_time(start_time)
		end_time_int = parse_time(end_time)
		if(start_time_int is None):
			message = f"Error: {start_time} is not a valid time."
		elif(end_time_int is None):
			message = f"Error: {end_time} is not a valid time."
		elif(start_time_int >= end_time_int):
			message = f"Error: end time must be after start time."
		else:
			con = sqlite.connect(DB_PATH)
			cur = con.cursor()
			result = cur.execute(f"SELECT name FROM {day} WHERE ( start_time >= ? AND start_time > ? ) OR ( end_time > ? AND end_time <= ? ) OR (start_time = ?)",
						(start_time_int, end_time_int, start_time_int, end_time_int, start_time_int)).fetchone()
			if(result is None):
				cur.execute(f"INSERT INTO {day} (name, desc, hosts, discord, poster, start_time, end_time, is_running) VALUES(?, ?, ?, ?, ?, ?, ?, 1)",
						(name, desc, hosts, host_discords, poster, start_time_int, end_time_int))
				con.commit()
				message = f"Show {name} has been added"
			else:
				message = f"Error: There is already a show named \"{result[0]}\" that overlaps with this timeslot."
			con.close()
	await context.response.send_message(message)

@tree.command(name="removeshow", description="Remove a show.", guild=discord.Object(id=GUILD_ID))
async def removeshow(context, name:str):
	if(not await check_admin(context)):
		return
	message = f"Error: no show named {name}"
	con = sqlite.connect(DB_PATH)
	cur = con.cursor()
	for day in days_of_week:
		result = cur.execute(f"SELECT start_time FROM {day} WHERE name = ? COLLATE NOCASE ORDER BY start_time", (name, )).fetchone()
		if(not result is None):
			cur.execute(f"DELETE FROM {day} WHERE start_time = ?", (result[0], ))
			con.commit()
			message = f"Show \"{name}\" has been deleted."
			break
	con.close()
	await context.response.send_message(message)

def format_property(property, value, day):
	if(property in ["start_time", "end_time"]):
		return f"<t:{get_timestamp(value, day)}:t>"
	if(property == "is_running"):
		return "true" if value == 1 else "false"
	return value

property_list = ["name", "desc", "hosts", "poster", "discord", "start_time", "end_time", "is_running"] 
@tree.command(name="setshowproperty", description="Edit a property of a show.", guild=discord.Object(id=GUILD_ID))
async def setshowproperty(context, name:str, property:str, value:str):
	if(not await check_admin(context)):
		return
	if(not property in property_list):
		await context.response.send_message(f"Error: \"{property}\" is not a valid property.\nThe valid properties are:\n```json\n{property_list}\n```")
		return
	if(property == "start_time" or property == "end_time"):
		parsed_value = parse_time(value)
		if(parsed_value is None):
			await context.response.send_message(f"Error: {value} is not a valid time.")
			return
		value = parsed_value
	if(property == "is_running"):
		value = value.lower()
		if(value == "true"):
			value = 1
		elif(value == "false"):
			value = 0
		else:
			await context.response.send_message(f"Error: is_running must be true or false.")
			return
	if(property == "discord"):
		value = " "+value.strip()+" "
	con = sqlite.connect(DB_PATH)
	cur = con.cursor()
	day = ""
	w = 0
	i = 0
	start_time = 0
	old_value = ""
	for d in days_of_week:
		result = cur.execute(f"SELECT {property}, name, start_time, end_time FROM {d} WHERE name = ? COLLATE NOCASE", (name, )).fetchone()
		if(not result is None):
			w = i
			day = d
			old_value = result[0]
			name = result[1]
			start_time = result[2]
			if(property in ["start_time", "end_time"]):
				valid = True
				if(property == "start_time"):
					if(value >= result[3]):
						valid = False
				if(property == "end_time"):
					if(value <= result[2]):
						valid = False
				if(not valid):
					await context.response.send_message("Error: start_time must be before end_time.")
					return
			break
		i += 1
	if(day == ""):
		await context.response.send_message(f"Error: no show named \"{name}\" found.")
		con.close()
		return
	cur.execute(f"UPDATE {day} SET {property} = ? WHERE start_time = ?", (value, start_time))
	con.commit()
	con.close()
	await context.response.send_message(f"Show \"{name}\" updated.\n**before**: {property} = {format_property(property, old_value, w)}\n**after**: {property} = {format_property(property, value, w)}")

@tree.command(name="getshowproperty", description="Get a property of a show.", guild=discord.Object(id=GUILD_ID))
async def getshowproperty(context, name:str, property:str):
	if(not await check_admin(context)):
		return
	if(not property in property_list):
		await context.response.send_message(f"Error: \"{property}\" is not a valid property.\nThe valid properties are:\n```json\n{property_list}\n```")
		return
	con = sqlite.connect(DB_PATH)
	cur = con.cursor()
	day = ""
	w = 0
	i = 0
	value = ""
	for d in days_of_week:
		result = cur.execute(f"SELECT {property}, name FROM {d} WHERE name = ? COLLATE NOCASE", (name, )).fetchone()
		if(not result is None):
			w = i
			day = d
			value = result[0]
			name = result[1]
			break
		i += 1
	con.close()
	if(day == ""):
		await context.response.send_message(f"Error: no show named \"{name}\" found.")
		return
	await context.response.send_message(f"Show \"{name}\"\n{property} = {format_property(property, value, w)}")

async def set_is_running(context, day, is_running):
	day = day.lower()
	username = (context.user.name+"#"+context.user.discriminator)
	con = sqlite.connect(DB_PATH)
	cur = con.cursor()
	dt = datetime.now(timezone("US/Eastern"))
	w = dt.weekday()
	weekend = False
	if(w >= 5):
		weekend = True
		w = 0
	time = dt.second+dt.minute*60+dt.hour*60*60
	
	start_time = -1
	if(day == ""):
		for i in range(w, len(days_of_week)+w):
			d = days_of_week[i%len(days_of_week)]
			if(i == w and not weekend):
				# this is the current day
				result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '% '||?||' %' AND is_running = ? AND end_time > ?", (username, 1-is_running, time)).fetchone()
				if(not result is None):
					day = d
					start_time = result[0]
					break
			result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '% '||?||' %' AND is_running = ?", (username, 1-is_running)).fetchone()
			if (not result is None):
				day = d
				start_time = result[0]
				break
	else:
		i = days_of_week.index(day)
		if(i == w and not weekend):
			# this is the current day
			result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '% '||?||' %' AND is_running = ? AND end_time > ? ORDER BY start_time", (username, 1-is_running, time)).fetchone()
			if(not result is None):
				day = d
				start_time = result[0]
		if(start_time != -1):
			result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '% '||?||' %' AND is_running = ? ORDER BY start_time", (username, 1-is_running)).fetchone()
			if (not result is None):
				day = d
				start_time = result[0]
	message = ""
	if(day == ""):
		if(is_running == 0):
			message = "Error: You do not have any shows running this week. (You might have already cancelled your show)"
		else:
			message = "Error: You do not have any cancelled shows running this week. (You might have already said you were doing your show)"
	elif(not day in days_of_week):
		message = "Error: Invalid day of the week."
	else:
		result = cur.execute(f"SELECT name, start_time, end_time FROM {day} WHERE is_running = ? AND start_time = ?", (1-is_running, start_time))
		row = result.fetchone()
		if(not row is None):
			cur.execute(f"UPDATE {day} SET is_running = ? WHERE is_running = ? AND start_time = ? LIMIT 1", (is_running, 1-is_running, start_time))
			show_name = row[0]
			time = row[1]
			end_time = row[2]
			if(is_running == 0):
				message = f"{context.user.display_name}'s show \"{show_name}\" <t:{get_timestamp(time, w, end_time)}:R> has been cancelled."
			else:
				message = f"{context.user.display_name}'s show \"{show_name}\" <t:{get_timestamp(time, w, end_time)}:R> will happen."
		else:
			if(is_running == 0):
				message = "Error: You do not have any shows running the selected timeframe. (You might have already cancelled your show)"
			else:
				message = "Error: You do not have any cancelled shows running during the selected timeframe. (You might have already said you were doing your show)"
		con.commit()
	con.close()
	await context.response.send_message(message)

@client.event
async def on_ready():
	await tree.sync(guild=discord.Object(id=GUILD_ID))

with open("token.secret", encoding='utf-8') as file:
	token = file.read()
	client.run(token)
