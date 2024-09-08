import re

import discord
import util
from datetime import datetime
import sqlite3 as sqlite
from ics import Calendar, Event

datetime_format = "%Y-%m-%d %H:%M"
human_time_format = "%I:%M %p / %H:%M"

questions = {
	'organizer_name': r'Full name and UCID - If the person running the event is not you, please list their name and UCID as well\.',
	'name': r'What is the name of the event\?',
	'club': r'What club or organization are you affiliated with\?',
	'date': r'What is the date of the event\?',
	'start': r'When does your event start\?',
	'end': r'When does your event end\?',
	'setup': r'When do you want us to set up for your event\?',
	'highlander_hub': r'Please provide the link to your Highlander Hub event page \(if available\):',
	'indoors': r'Is the event outdoor or indoor\?',
	'location': r'Where, specifically, is the event located\?',
	'dress_code': r'What is the dress code for your event\?',
	'size_audience': r'What is the estimated size of the event\? Who is the general audience\? \(Students, children, faculty, etc\)',
	'additional_equipment': r'Please list any additional equipment that you may need \(mic stands, more than 2 mics, speakers facing in all directions, tarps, AC power, headphones, external outputs, extra monitors, etc\)',
	'playlist_mood': r'Please link a playlist \(preferred\) or describe a mood/genre you want for the event',
	'announcement_people': r'Please list the names of all people who are qualified to make announcements or perform at this event\. WJTB strictly prohibits anyone from using the microphones or equipment at the event- unless they are on this list\. WJTB is not liable for any damage to WJTB equipment caused by these people\.',
	'cohost_agreement': r'If available to fulfill your request, WJTB must be listed as a cohost on your event for Student Senate purposes',
}

def parse_response_field(field_name, content):
	content = content+"\n"
	result = re.search(r'(?i) ?\*\* ?'+field_name+r' ?\*\* ?\n ?((?:[^\*]*\n)*) ?\n? ?((\*\*)|$)', content, re.M)
	return None if result is None else result.group(1).strip()

def create_live_events_table(con, cur):
	cur.execute("CREATE TABLE IF NOT EXISTS live_events (name TEXT, setup TEXT, start TEXT, end TEXT, organizer_name TEXT, club TEXT, highlander_hub TEXT, location TEXT, indoors TEXT, dress_code TEXT, size_audience TEXT, additional_equipment TEXT, playlist_mood TEXT, announcement_people TEXT, cohost_agreement TEXT)")
	con.commit()

def add_calendar_event(embed_text):
	date = parse_response_field(questions['date'], embed_text)
	if(date is None):
		return "Couldn't parse date"
	try:
		setup = datetime.strptime(date+' '+parse_response_field(questions['setup'], embed_text), datetime_format).strftime(datetime_format)
	except ValueError as e:
		print(e)
		return "Unknown format for setup time"
	if(setup is None):
		return "Couldn't parse setup"
	try:
		start = datetime.strptime(date+' '+parse_response_field(questions['start'], embed_text), datetime_format).strftime(datetime_format)
	except ValueError:
		return "Unknown format for start time"
	if(start is None):
		return "Couldn't parse start"
	try:
		end = datetime.strptime(date+' '+parse_response_field(questions['end'], embed_text), datetime_format).strftime(datetime_format)
	except ValueError:
		return "Unknown format for end time"
	if(end is None):
		return "Couldn't parse end time"
	name = parse_response_field(questions['name'], embed_text)
	if(name is None):
		return "Couldn't parse name"
	organizer_name = parse_response_field(questions['organizer_name'], embed_text)
	if(organizer_name is None):
		return "Couldn't parse organizer name"
	club = parse_response_field(questions['club'], embed_text)
	if(club is None):
		return "Couldn't parse club"
	highlander_hub = parse_response_field(questions['highlander_hub'], embed_text)
	if(highlander_hub is None):
		return "Couldn't parse highlander hub"
	location = parse_response_field(questions['location'], embed_text)
	if(location is None):
		return "Couldn't parse location"
	indoors = parse_response_field(questions['indoors'], embed_text)
	if(indoors is None):
		return "Couldn't parse indoors"
	dress_code = parse_response_field(questions['dress_code'], embed_text)
	if(dress_code is None):
		return "Couldn't parse dress code"
	size_audience = parse_response_field(questions['size_audience'], embed_text)
	if(size_audience is None):
		return "Couldnt parse size/audience"
	additional_equipment = parse_response_field(questions['additional_equipment'], embed_text)
	if(additional_equipment is None):
		return "Couldn't parse additional equipment"
	playlist_mood = parse_response_field(questions['playlist_mood'], embed_text)
	if(playlist_mood is None):
		return "Couldn't parse playlist/mood"
	announcement_people = parse_response_field(questions['announcement_people'], embed_text)
	if(announcement_people is None):
		return "Couldn't parse announcement people"
	cohost_agreement = parse_response_field(questions['cohost_agreement'], embed_text)
	if(cohost_agreement is None):
		return "Couldn't parse cohost agreement"
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	create_live_events_table(con, cur)
	result = cur.execute("SELECT name FROM live_events WHERE start = ? AND name = ?", (start, name)).fetchone()
	if(result is None):
		cur.execute("INSERT INTO live_events "
				"(name, setup, start, end, organizer_name, club, highlander_hub, location, indoors, dress_code, size_audience, additional_equipment, playlist_mood, announcement_people, cohost_agreement) "
				"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
				(name, setup, start, end, organizer_name, club, highlander_hub, location, indoors, dress_code, size_audience, additional_equipment, playlist_mood, announcement_people, cohost_agreement)
			)
	else:
		con.close()
		return "Event already in calendar"
	con.commit()
	con.close()
	return None

def remove_calendar_event(name, date):
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	result = cur.execute("DELETE FROM live_events WHERE start LIKE ? AND name = ? COLLATE NOCASE RETURNING name", (date.strftime("%Y-%m-%d%%"), name))
	row = result.fetchone()
	output = ""
	while(not row is None):
		output = output + f'"{row[0]}"\n'
		row = result.fetchone()
	con.commit()
	con.close()
	return output

def export_calendar():
	con = sqlite.connect(util.DB_PATH)
	cur = con.cursor()
	create_live_events_table(con, cur)
	result = cur.execute("SELECT name, setup, start, end, organizer_name, club, highlander_hub, location, indoors, dress_code, size_audience, additional_equipment, playlist_mood, announcement_people, cohost_agreement FROM live_events")
	row = result.fetchone()
	calendar = Calendar()
	while(not row is None):
		name = row[0]
		setup = datetime.strptime(row[1], datetime_format)
		start = datetime.strptime(row[2], datetime_format)
		end = datetime.strptime(row[3], datetime_format)
		organizer_name = row[4]
		club = row[5]
		highlander_hub = row[6]
		location = row[7]
		indoors = row[8]
		dress_code = row[9]
		size_audience = row[10]
		additional_equipment = row[11]
		playlist_mood = row[12]
		announcement_people = row[13]
		cohost_agreement = row[14]

		event = Event(name=name,
					begin=start,
					end=end,
					location=location,
					description=(
						f'Setup Time: {setup.strftime(human_time_format)}\n'
						f'Start Time: {start.strftime(human_time_format)}\n'
						f'End Time: {end.strftime(human_time_format)}\n'
						f'Organizer: {organizer_name}\n'
						f'Club: {club}\n'
						f'{indoors}\n'
						f'Dress Code: {dress_code}\n'
						f'Size/Audience: {size_audience}\n'
						f'Additional Equipment: {additional_equipment}\n'
						f'Playlist/Mood: {playlist_mood}\n'
						f'People who can make announcements: {announcement_people}\n'
						f'Highlander Hub: {highlander_hub}\n'
						f'Cohost Agreement: {cohost_agreement}\n'
					)
				)

		calendar.events.add(event)

		row = result.fetchone()
	con.close()
	return calendar.serialize_iter()

def add_commands(tree):
	@tree.command(name="removeliveevent", description="Remove a live event from the calendar.", guild=discord.Object(id=util.GUILD_ID))
	async def removeliveevent(context, name: str, date: str):
		events = remove_calendar_event(name, date)
		if(events == ""):
			await context.response.send_message(
				f'No live event found with name "{name}" and date {date}\n'
				f'Make sure the date is in YYYY-MM-DD format.\n'
				f'Name is case insensitive')
		else:
			await context.response.send_message(
				f'These live events have been removed from the calendar:\n{events}\n\n'
				f'It may take a few minutes for the update to propagate.')
