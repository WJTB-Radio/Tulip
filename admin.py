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

import util
import output

def add_commands(tree):
	@tree.command(name="addshow", description="Add a show.", guild=discord.Object(id=util.GUILD_ID))
	async def addshow(context, name:str, hosts:str, host_discords:str, desc:str, poster:str, day:str, start_time:str, end_time:str):
		if(not await util.check_admin(context)):
			return
		host_discords = ":"+host_discords.strip()+":"
		day = day.lower()
		message = ""
		if(not day in util.days_of_week):
			message = f"\"{day}\" is not a valid day of the week.\nThe valid days of the week are monday, tuesday, wednesday, thursday, and friday."
		else:
			start_time_int = util.parse_time(start_time)
			end_time_int = util.parse_time(end_time)
			if(start_time_int is None):
				message = f"Error: {start_time} is not a valid time."
			elif(end_time_int is None):
				message = f"Error: {end_time} is not a valid time."
			elif(start_time_int >= end_time_int):
				message = f"Error: end time must be after start time."
			else:
				con = sqlite.connect(util.DB_PATH)
				cur = con.cursor()
				poster = util.convert_image(poster)
				result = cur.execute(f"SELECT name FROM {day} WHERE ( start_time >= ? AND start_time < ? ) OR ( end_time > ? AND end_time <= ? ) OR (start_time = ?)",
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
		output.update()
		await asyncio.sleep(5)
		output.push()

	@tree.command(name="removeshow", description="Remove a show.", guild=discord.Object(id=util.GUILD_ID))
	async def removeshow(context, name:str):
		if(not await util.check_admin(context)):
			return
		message = f"Error: no show named {name}"
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		for day in util.days_of_week:
			result = cur.execute(f"SELECT start_time FROM {day} WHERE name = ? COLLATE NOCASE ORDER BY start_time", (name, )).fetchone()
			if(not result is None):
				cur.execute(f"DELETE FROM {day} WHERE start_time = ?", (result[0], ))
				con.commit()
				message = f"Show \"{name}\" has been deleted."
				break
		con.close()
		await context.response.send_message(message)
		output.update()
		await asyncio.sleep(5)
		output.push()

	@tree.command(name="setshowproperty", description="Edit a property of a show.", guild=discord.Object(id=util.GUILD_ID))
	async def setshowproperty(context, name:str, property:str, value:str):
		if(not await util.check_admin(context)):
			return
		if(not property in util.property_list):
			await context.response.send_message(f"Error: \"{property}\" is not a valid property.\nThe valid properties are:\n```json\n{util.property_list}\n```")
			return
		if(property == "start_time" or property == "end_time"):
			parsed_value = util.parse_time(value)
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
			value = ":"+value.strip()+":"
		if(property == "poster"):
			value = util.convert_image(value)
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		day = ""
		w = 0
		i = 0
		start_time = 0
		old_value = ""
		for d in util.days_of_week:
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
		await context.response.send_message(f"Show \"{name}\" updated.\n**before**: {property} = {util.format_property(property, old_value, w)}\n**after**: {property} = {util.format_property(property, value, w)}")
		output.update()
		await asyncio.sleep(5)
		output.push()

	@tree.command(name="getshowproperty", description="Get a property of a show.", guild=discord.Object(id=util.GUILD_ID))
	async def getshowproperty(context, name:str, property:str):
		if(not await util.check_admin(context)):
			return
		if(not property in util.property_list):
			await context.response.send_message(f"Error: \"{property}\" is not a valid property.\nThe valid properties are:\n```json\n{util.property_list}\n```")
			return
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		day = ""
		w = 0
		i = 0
		value = ""
		for d in util.days_of_week:
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
		await context.response.send_message(f"Show \"{name}\"\n{property} = {util.format_property(property, value, w)}")

