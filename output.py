import util

import json
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

import live_events_calendar

def shows(day):
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = cur.execute(f"SELECT name, desc, hosts, poster, start_time, end_time, is_running FROM {day}")
	show_list = []
	row = result.fetchone()
	while(not row is None):
		show = {
				"name":row[0],
				"desc":row[1],
				"hosts":row[2],
				"poster":row[3],
				"start_time":row[4],
				"end_time":row[5],
				"is_running":row[6],
				}
		show_list.append(show)
		row = result.fetchone()
	con.close()
	return json.dumps({
			"day":day,
			"shows":show_list
		})

def fix_line_breaks(text):
	return text.replace("<br/>", "\n")

def past_events():
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = cur.execute(f"SELECT name, desc, date, images FROM past_events ORDER BY date")
	events = []
	row = result.fetchone()
	while(not row is None):
		date = datetime.strptime(row[2], "%Y/%m/%d").strftime("%A, %B %d %Y")
		event = {
				"name":row[0],
				"desc":fix_line_breaks(row[1]),
				"date":date,
				"images":row[3].split(" "),
				}
		events.append(event)
		row = result.fetchone()
	return json.dumps({
			"events":events,
			})

def staff():
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = cur.execute(f"SELECT name, flavor, position, image FROM staff ORDER BY seder")
	staff = []
	row = result.fetchone()
	while(not row is None):
		s = {
				"name":row[0],
				"flavor":row[1],
				"position":row[2],
				"image":row[3],
				}
		staff.append(s)
		row = result.fetchone()
	return json.dumps({
			"staff":staff,
			})

def gallery(limit):
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = None
	if(limit is None):
		result = cur.execute("SELECT image, date_taken, caption FROM gallery ORDER BY date_taken DESC")
	else:
		result = cur.execute("SELECT image, date_taken, caption FROM gallery ORDER BY date_taken DESC LIMIT ?", (limit, ))
	photos = []
	row = result.fetchone()
	while(not row is None):
		date_taken = 0
		try:
			date_taken = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f%z').strftime('%A, %B %d %Y')
		except ValueError:
			# for some reason sometimes we dont get subsecond info?
			date_taken = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S').strftime('%A, %B %d %Y')
		p = {
				"image":row[0],
				"date_taken": date_taken,
				"caption":row[2],
				}
		photos.append(p)
		row = result.fetchone()
	return json.dumps({
			"photos":photos,
			})

def get_wait_time():
	now = datetime.now(timezone("US/Eastern"))
	last_run_time = now.replace(minute=now.minute // 5 * 5, second=0, microsecond=0)
	next_run_time = last_run_time + timedelta(minutes=5, seconds=30) # give an extra few seconds of leeway
	return (next_run_time - now).total_seconds()

def update():
	for day in util.days_of_week:
		with open(f"{util.show_data_path}/{day}.json", "w") as file:
			file.write(shows(day))
	with open(f"{util.show_data_path}/past_events.json", "w") as file:
		file.write(past_events())
	with open(f"{util.show_data_path}/staff.json", "w") as file:
		file.write(staff())
	with open(f"{util.show_data_path}/gallery.json", "w") as file:
		file.write(gallery(None))
	with open(f"{util.show_data_path}/gallery_top.json", "w") as file:
		file.write(gallery(3))
	with open(f"{util.show_data_path}/live_events_calendar.ics", "w") as file:
		file.writelines(live_events_calendar.export_calendar())

def push():
	os.system(f"{util.show_data_path}/push.sh")	

async def update_loop():
	while True:
		update()
		# give files time to update
		await asyncio.sleep(5)
		push()
		# run again every 5 minutes
		# a better solution would be to use the end time of the show, but this works fine
		# git will detect when nothing changed and act appropriately
		# and this only runs every 5 mintues which should be fine
		wait_time = get_wait_time()
		await asyncio.sleep(wait_time)


