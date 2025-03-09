import { DatabaseSync } from "node:sqlite";
import { env } from "../config.ts";

function connectDb() {
	const db = new DatabaseSync(env.DB_PATH);
	db.exec(`
		CREATE TABLE IF NOT EXISTS live_events(
			name TEXT,
			setup TEXT,
			start TEXT,
			end TEXT,
			organizer_name TEXT,
			club TEXT,
			highlander_hub TEXT,
			location TEXT,
			indoors TEXT,
			dress_code TEXT,
			size_audience TEXT,
			additional_equipment TEXT,
			playlist_mood TEXT,
			announcement_people TEXT,
			cohost_agreement TEXT
		);
	`);
	return db;
}

export interface LiveEvent {
	name: string;
	setup: string;
	start: string;
	end: string;
	organizer_name: string;
	club: string;
	highlander_hub: string;
	location: string;
	indoors: string;
	dress_code: string;
	size_audience: string;
	additional_equipment: string;
	playlist_mood: string;
	announcement_people: string;
	cohost_agreement: string;
}

export function addLiveEvent(
	event: LiveEvent,
): LiveEvent[] {
	const db = connectDb();
	db.prepare(`
		INSERT INTO live_events (
			name,
			setup,
			start,
			end,
			organizer_name,
			club,
			highlander_hub,
			location,
			indoors,
			dress_code,
			size_audience,
			additional_equipment,
			playlist_mood,
			announcement_people,
			cohost_agreement
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
	`).run(
		event.name,
		event.setup,
		event.start,
		event.end,
		event.organizer_name,
		event.club,
		event.highlander_hub,
		event.location,
		event.indoors,
		event.dress_code,
		event.size_audience,
		event.additional_equipment,
		event.playlist_mood,
		event.announcement_people,
		event.cohost_agreement,
	);
	const events = selectLiveEvents(db);
	db.close();
	return events;
}

function selectLiveEvents(db: DatabaseSync): LiveEvent[] {
	return db.prepare(`
		SELECT 
			name,
			setup,
			start,
			end,
			organizer_name,
			club,
			highlander_hub,
			location,
			indoors,
			dress_code,
			size_audience,
			additional_equipment,
			playlist_mood,
			announcement_people,
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
