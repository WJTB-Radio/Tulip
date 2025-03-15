import { addLiveEvent, getLiveEvents, LiveEvent } from "./db.ts";
import ical from "ical-generator";
import { format, parse } from "date-fns";
import { writeFile } from "node:fs/promises";
import { env } from "../config.ts";

export function parseDate(s: string) {
	return parse(s, "yyyy-MM-dd HH:mm", new Date(0));
}

function formatTimeHuman(d: Date) {
	return format(d, "hh:mm / HH:mm");
}

export function addEventToCalendar(event: LiveEvent) {
	outputCalendar(addLiveEvent(event));
}

export function startupCalendar() {
	outputCalendar(getLiveEvents());
}

export function outputCalendar(events: LiveEvent[]) {
	const calEvents = events.map((event) => {
		const setup = parseDate(event.setup);
		const start = parseDate(event.start);
		const end = parseDate(event.end);
		return {
			summary: event.name,
			start: setup,
			end,
			location: event.location,
			url: event.highlander_hub,
			description: `\
Setup Time: ${formatTimeHuman(setup)}
Start Time: ${formatTimeHuman(start)}
End Time: ${formatTimeHuman(end)}
Organizer: ${event.organizer_name}
Club: ${event.club}
${event.indoors}
Dress Code: ${event.dress_code}
Size/Audience: ${event.size_audience}
Additional Equipment: ${event.additional_equipment}
Playlist/Mood: ${event.playlist_mood}
People who can make announcements: ${event.announcement_people}
Highlander Hub: ${event.highlander_hub}
Cohost Agreement: ${event.cohost_agreement}
`,
		};
	});
	const calendar = ical({
		name: "WJTB Live Events Calendar",
		events: calEvents,
	});
	writeFile(env.CALENDAR_PATH, calendar.toString());
}

const questions = {
	"organizer_name":
		"Full name and UCID - If the person running the event is not you, please list their name and UCID as well\\.",
	"name": "What is the name of the event\\?",
	"club": "What club or organization are you affiliated with\\?",
	"date": "What is the date of the event\\?",
	"start": "When does your event start\\?",
	"end": "When does your event end\\?",
	"setup": "When do you want us to set up for your event\\?",
	"highlander_hub":
		"Please provide the link to your Highlander Hub event page \\(if available\\):",
	"indoors": "Is the event outdoor or indoor\\?",
	"location": "Where, specifically, is the event located\\?",
	"dress_code": "What is the dress code for your event\\?",
	"size_audience":
		"What is the estimated size of the event\\? Who is the general audience\\? \\(Students, children, faculty, etc\\)",
	"additional_equipment":
		"Please list any additional equipment that you may need \\(mic stands, more than 2 mics, speakers facing in all directions, tarps, AC power, headphones, external outputs, extra monitors, etc\\)",
	"playlist_mood":
		"Please link a playlist \\(preferred\\) or describe a mood/genre you want for the event",
	"announcement_people":
		"Please list the names of all people who are qualified to make announcements or perform at this event\\. WJTB strictly prohibits anyone from using the microphones or equipment at the event- unless they are on this list\\. WJTB is not liable for any damage to WJTB equipment caused by these people\\.",
	"cohost_agreement":
		"If available to fulfill your request, WJTB must be listed as a cohost on your event for Student Senate purposes",
};

function parseQuestion(
	question: keyof typeof questions,
	text: string,
): string | undefined {
	return new RegExp(
		" ?\\*\\* ?" + questions[question] +
			" ?\\*\\* ?\\n ?(?<answer>(?:[^\\*]*\\n)*) ?\\n? ?((\\*\\*)|$)",
	).exec(text + "\n")?.groups?.answer.trim();
}

export function parseLiveEvent(text: string): LiveEvent | undefined {
	let success = true;
	const answers = (Object.keys(questions) as (keyof typeof questions)[]).reduce(
		(acc, field) => {
			const answer = parseQuestion(field, text);
			if (answer == undefined) {
				success = false;
				return acc;
			}
			acc[field] = answer;
			return acc;
		},
		{} as Record<keyof typeof questions, string>,
	);
	if (!success) return undefined;
	return {
		...answers,
		start: `${answers.date} ${answers.start}`,
		end: `${answers.date} ${answers.end}`,
		setup: `${answers.date} ${answers.setup}`,
	};
}
