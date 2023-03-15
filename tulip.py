#!/bin/python3

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

DB_PATH = sys.argv[1]#"../wjtb_db/database.sqlite3"
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
		print(f"cur_w = {cur_w}, w = {w} 1 adding 7")
		w += 7
	cur_time_seconds = cur_dt.second+cur_dt.minute*60+cur_dt.hour*60*60
	if(w == cur_w and cur_time_seconds > end_time_seconds):
		print(f"adding 7 2 cur_time_seconds = {cur_time_seconds} time_seconds = {time_seconds}")
		w += 7
	cur_date = cur_dt.date()
	d = cur_date + timedelta(days=w-cur_w)
	t = time(hour=int(time_seconds/(60*60)), minute=int((time_seconds/60)%60))
	dt = datetime.combine(d, t)
	timestamp = dt.timestamp()
	return int(timestamp)

def format_show(name, hosts, desc, day, start_time, end_time, is_running):
	w = days_of_week.index(day)
	time = f"<t:{get_timestamp(start_time, w)}:t>-<t:{get_timestamp(end_time, w)}:t>"
	running = "" if is_running == 1 else "**The next show has been cancelled.**"
	return f"**{name}**\n{time}\n**hosted by**\n{hosts}\n**description**\n{desc}\n\n{running}"

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
		result = cur.execute(f"SELECT name FROM {day} WHERE name = ? COLLATE NOCASE", (name, )).fetchone()
		if(not result is None):
			cur.execute(f"DELETE FROM {day} WHERE name = ? COLLATE NOCASE", (name, ))
			con.commit()
			message = f"Show \"{name}\" has been deleted."
			break
	con.close()
	await context.response.send_message(message)

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
	
	if(day == ""):
		for i in range(w, len(days_of_week)+w):
			d = days_of_week[i%len(days_of_week)]
			result = 0
			if(i == w and not weekend):
				# this is the current day
				result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '% '||?||' %' AND is_running = ? AND end_time > ?", (username, 1-is_running, time))
			else:
				# this is a day in the future
				result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '% '||?||' %' AND is_running = ?", (username, 1-is_running))
			if(not result.fetchone() is None):
				day = d
				break
	message = ""
	if(day == ""):
		if(is_running == 0):
			message = "Error: You do not have any shows running this week. (You might have already cancelled your show)"
		else:
			message = "Error: You do not have any cancelled shows running this week. (You might have already said you were doing your show)"
	elif(not day in days_of_week):
		message = "Error: Invalid day of the week."
	else:
		result = cur.execute(f"SELECT name, start_time, end_time FROM {day} WHERE is_running = ? AND discord LIKE '% '||?||' %' ORDER BY start_time", (1-is_running, username))
		row = result.fetchone()
		if(not row is None):
			cur.execute(f"UPDATE {day} SET is_running = ? WHERE is_running = ? AND discord LIKE '% '||?||' %' ORDER BY start_time LIMIT 1", (is_running, 1-is_running, username))
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
