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
import subprocess

GUILD_ID = 172047876384358400
property_list = ["name", "desc", "hosts", "poster", "discord", "start_time", "end_time", "is_running"] 
days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday"] 

show_data_path = ""
DB_PATH = ""

def get_timestamp(time_seconds, w, end_time_seconds=None):
	if(end_time_seconds is None):
		end_time_seconds = time_seconds
	cur_dt = datetime.now(timezone("America/New_York"))
	cur_w = cur_dt.weekday()
	if(w < cur_w):
		w += 7
	cur_time_seconds = cur_dt.second+cur_dt.minute*60+cur_dt.hour*60*60
	if(w == cur_w and cur_time_seconds > end_time_seconds):
		w += 7
	cur_date = cur_dt.date()
	d = cur_date + timedelta(days=(w-cur_w))
	t = time(hour=int(time_seconds/(60*60)), minute=int((time_seconds/60)%60))
	dt = datetime.combine(d, t)
	timestamp = dt.timestamp()
	return int(timestamp)

def format_show(name, hosts, desc, day, start_time, end_time, is_running):
	w = days_of_week.index(day)
	time = f"<t:{get_timestamp(start_time, w, end_time)}:t>-<t:{get_timestamp(end_time, w)}:t>"
	running = "" if is_running == 1 else "**The next show has been cancelled.**"
	return f"**{name}**\n{time}\n{day}\n**hosted by**\n{hosts}\n**description**\n{desc}\n\n{running}"

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

def format_property(property, value, day):
	if(property in ["start_time", "end_time"]):
		return f"<t:{get_timestamp(value, day)}:t>"
	if(property == "is_running"):
		return "true" if value == 1 else "false"
	return value

def convert_image(url):
	if(url.find("wjtb.njit.edu") != -1 or url.find("raw.githubusercontent.com") != -1):
		# we dont need to convert our own urls or urls we've already converted
		return url
	# discord doesnt work as a cdn anymore so we have to use github instead
	subprocess_result = subprocess.run(["./resize.sh", url], capture_output=True)
	url = subprocess_result.stdout.decode("utf-8").strip()
	if(url == ""):
		# something went wrong, aka this image is invalid
		return ""
	url = "https://raw.githubusercontent.com/WJTB-Radio/ShowData/master/images/" + url
	return url
