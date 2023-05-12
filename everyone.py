from util import *

def add_commands(tree):
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

