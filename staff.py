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
	@tree.command(name="addstaff", description="Remove a staff member.", guild=discord.Object(id=util.GUILD_ID))
	async def addstaff(context, name:str, flavor:str, position:str, image:str, seder:int):
		if(not await util.check_admin(context)):
			return
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		result = cur.execute("SELECT * FROM staff WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
		if(not result is None):
			await context.response.send_message(f"Error: There is already a staff member named \"{name}\"")
			con.close()
			return
		cur.execute("INSERT INTO staff(name, flavor, position, image, seder) VALUES(?, ?, ?, ?, ?)", (name, flavor, position, image, seder))
		con.commit()
		con.close()
		await context.response.send_message(f"{name} has been added to the staff page.\nIt may take a few minutes to update on the website.")
		output.update()
		await asyncio.sleep(5)
		output.push()
	
	@tree.command(name="removestaff", description="Add a staff member.", guild=discord.Object(id=util.GUILD_ID))
	async def removestaff(context, name:str):
		if(not await util.check_admin(context)):
			return
		message = ""
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		result = cur.execute("SELECT * FROM staff WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
		if(result is None):
			message = f"Error: No staff member named \"{name}\" found."
		else:
			cur.execute("DELETE FROM staff WHERE name = ? COLLATE NOCASE", (name,))
			con.commit()
			message = f"\"{name}\" has been removed from the staff page.\nIt may take a few minutes to update on the website."
		con.close()
		await context.response.send_message(message)
		output.update()
		await asyncio.sleep(5)
		output.push()
	
	@tree.command(name="editstaff", description="Edit a staff member.", guild=discord.Object(id=util.GUILD_ID))
	async def editpastevent(context, name:str, property:str, value:str):
		if(not await util.check_admin(context)):
			return
		properties = ["name", "flavor", "position", "image", "seder"]
		if(not property in properties):
			await context.response.send_message(f"\"{property}\" is not a valid property.\nThe valid properties are ```{properties}```")
			return
		con = sqlite.connect(util.DB_PATH)
		cur = con.cursor()
		result = cur.execute(f"SELECT {property} FROM staff WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
		if(result is None):
			await context.response.send_message(f"Error: No staff member named \"{name}\" found.")
			con.close()
			return
		if(property == "seder"):
			try:
				value = int(value)
			except ValueError:
				await context.response.send_message(f"Error: {property} must be an integer.")
				con.close()
				return
		cur.execute(f"UPDATE staff SET {property} = ? WHERE name = ? COLLATE NOCASE", (value, name))
		con.commit()
		con.close()
		await context.response.send_message(f"Staff \"{name}\" updated.\n**before**: {property} = {result[0]}\n**after**: {property} = {value}")
		output.update()
		await asyncio.sleep(5)
		output.push()
