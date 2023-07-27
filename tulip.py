#!/bin/python3

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

import output
import util
import djs
import admin
import everyone
import past_events
import staff

if(len(sys.argv) != 3):
	print("please supply a path to the sqlite3 database and a path to the showdata repository as commandline arguments")
	sys.exit()

util.show_data_path = sys.argv[2]
util.DB_PATH = sys.argv[1]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

everyone.add_commands(tree)
djs.add_commands(tree)
admin.add_commands(tree)
past_events.add_commands(tree)
staff.add_commands(tree)

@client.event
async def on_ready():
	client.loop.create_task(output.update_loop())
	await tree.sync(guild=discord.Object(id=util.GUILD_ID))

with open("token.secret", encoding='utf-8') as file:
	token = file.read()
	client.run(token)

