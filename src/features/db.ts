import { DatabaseSync } from "node:sqlite";
import { env } from "../config.ts";

function connectDb() {
	const db = new DatabaseSync(env.DB_PATH);
	db.exec(`
		CREATE TABLE IF NOT EXISTS live_events(
			organizer_name TEXT,
			announcement_people TEXT,
			name TEXT,
			club TEXT,
			date TEXT,
			start TEXT,
			end TEXT,
			setup TEXT,
			highlander_hub TEXT,
			indoors TEXT,
			location TEXT,
			dress_code TEXT,
			size_audience TEXT,
			additional_equipment TEXT,
			playlist_mood TEXT,
			cohost_agreement TEXT
		);
	`);
	return db;
}

export interface LiveEvent {
	organizer_name: string;
	announcement_people: string;
	name: string;
	club: string;
	date: string;
	start: string;
	end: string;
	setup: string;
	highlander_hub: string;
	indoors: string;
	location: string;
	dress_code: string;
	size_audience: string;
	additional_equipment: string;
	playlist_mood: string;
	cohost_agreement: string;
}

export function addLiveEvent(
	event: LiveEvent,
): LiveEvent[] {
	const db = connectDb();
	db.prepare(`
		INSERT INTO live_events (
			organizer_name,
			announcement_people,
			name,
			club,
			date,
			start,
			end,
			setup,
			highlander_hub,
			indoors,
			location,
			dress_code,
			size_audience,
			additional_equipment,
			playlist_mood,
			cohost_agreement
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
	`).run(
		event.organizer_name,
		event.announcement_people,
		event.name,
		event.club,
		event.date,
		event.start,
		event.end,
		event.setup,
		event.highlander_hub,
		event.indoors,
		event.location,
		event.dress_code,
		event.size_audience,
		event.additional_equipment,
		event.playlist_mood,
		event.cohost_agreement,
	);
	const events = selectLiveEvents(db);
	db.close();
	return events;
}

function selectLiveEvents(db: DatabaseSync): LiveEvent[] {
	return db.prepare(`
		SELECT 
			organizer_name,
			announcement_people,
			name,
			club,
			date,
			start,
			end,
			setup,
			highlander_hub,
			indoors,
			location,
			dress_code,
			size_audience,
			additional_equipment,
			playlist_mood,
			cohost_agreement
		FROM live_events
	`).all() as LiveEvent[];
}

export function getLiveEvents() {
	const db = connectDb();
	const events = selectLiveEvents(db);
	db.close();
	return events;
}
