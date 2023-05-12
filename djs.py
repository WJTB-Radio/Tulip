from util import *

# DJ commands go in this file
def add_commands(tree):
	@tree.command(name="notdoingmyshow", description="Run this command to announce that you aren't doing your show this week.", guild=discord.Object(id=GUILD_ID))
	async def notdoingmyshow(context, day:str=""):
		await set_is_running(context, day, 0)
	
	@tree.command(name="doingmyshow", description="Run this command to announce that you are doing your show this week.", guild=discord.Object(id=GUILD_ID))
	async def doingmyshow(context, day:str=""):
		await set_is_running(context, day, 1)

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
				result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '%:'||?||':%' AND is_running = ? AND end_time > ?", (username, 1-is_running, time)).fetchone()
				if(not result is None):
					day = d
					start_time = result[0]
					break
			result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '%:'||?||':%' AND is_running = ?", (username, 1-is_running)).fetchone()
			if (not result is None):
				day = d
				start_time = result[0]
				break
	else:
		i = days_of_week.index(day)
		if(i == w and not weekend):
			# this is the current day
			result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '%:'||?||':%' AND is_running = ? AND end_time > ? ORDER BY start_time", (username, 1-is_running, time)).fetchone()
			if(not result is None):
				day = d
				start_time = result[0]
		if(start_time != -1):
			result = cur.execute(f"SELECT start_time FROM {d} WHERE discord LIKE '%:'||?||':%' AND is_running = ? ORDER BY start_time", (username, 1-is_running)).fetchone()
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
			cur.execute(f"UPDATE {day} SET is_running = ? WHERE is_running = ? AND start_time = ?", (is_running, 1-is_running, start_time))
			show_name = row[0]
			time = row[1]
			end_time = row[2]
			if(is_running == 0):
				message = f"{context.user.display_name}'s show \"{show_name}\" has been cancelled.\nIt may take a few minutes to update on the site.\nMake sure to use ```/doingmyshow``` next week to uncancel your show."
			else:
				message = f"{context.user.display_name}'s show \"{show_name}\" has been uncancelled.\nIt may take a few minutes to update on the site."
		else:
			if(is_running == 0):
				message = "Error: You do not have any shows running the selected timeframe. (You might have already cancelled your show)"
			else:
				message = "Error: You do not have any cancelled shows running during the selected timeframe. (You might have already said you were doing your show)"
		con.commit()
	con.close()
	await context.response.send_message(message)
	update_shows()
	await asyncio.sleep(5)
	push_shows()

