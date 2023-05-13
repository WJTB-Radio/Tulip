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
	@tree.command(name="addpastevent", description="Add a past event.", guild=discord.Object(id=util.GUILD_ID))
	async def addpastevent(context, name:str, desc:str, date:str, images:str):
		if(not await util.check_admin(context)):
			return
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		cur.execute("INSERT INTO past_events(name, desc, date, images) VALUES(?, ?, ?, ?)", (name, desc, date, images))
		con.commit()
		con.close()
		await context.response.send_message(f"{name} has been added to the past events page.\nIt may take a few minutes to update on the website.")
		output.update()
		await asyncio.sleep(5)
		output.push()
	
	@tree.command(name="removepastevent", description="Add a past event.", guild=discord.Object(id=util.GUILD_ID))
	async def removepastevent(context, name:str):
		if(not await util.check_admin(context)):
			return
		message = ""
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		result = cur.execute("SELECT FROM past_events WHERE name = ?", (name,)).fetchone()
		if(result is None):
			message = f"Error: No past event called \"{name}\" found."
		else:
			cur.execute("DELETE FROM past_events WHERE name = ?", (name,))
			con.commit()
			message = f"\"{name}\" has been removed from the past events page."
		con.close()
		await context.response.send_message(message)
		output.update()
		await asyncio.sleep(5)
		output.push()
	
	@tree.command(name="editpastevent", description="Add a past event.", guild=discord.Object(id=util.GUILD_ID))
	async def editpastevent(context, name:str, property:str, value:str):
		if(not await util.check_admin(context)):
			return
		properties = ["name", "desc", "date", "images"]
		if(not property in properties):
			await context.response.send_message(f"\"{property}\" is not a valid property.\nThe valid properties are ```{properties}```")
			return
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		result = cur.execute(f"SELECT {property} FROM past_events WHERE name = ?", (name,)).fetchone()
		if(result is None):
			await context.response.send_message(f"Error: No past event called \"{name}\" found.")
			con.close()
			return
		cur.execute(f"UPDATE past_events SET {property} = ? WHERE name = ?", (value, name))
		con.commit()
		con.close()
		await context.response.send_message(f"Past event \"{name}\" updated.\n**before**: {property} = {result[0]}\n**after**: {property} = {value}")
		output.update()
		await asyncio.sleep(5)
		output.push()
