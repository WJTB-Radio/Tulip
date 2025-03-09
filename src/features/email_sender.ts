import nodemailer from "nodemailer";
import { MessageTypes } from "@discordeno/types";
import { bot } from "../bot.ts";
import { sendErrorReply, sendReply } from "../utils/error_sender.ts";
import { parseMessage } from "../utils/message_parser.ts";
import { format } from "date-fns/format";
import { env } from "../config.ts";
import {
	addEventToCalendar,
	parseDate,
	parseLiveEvent,
} from "./event_calendar.ts";

const exampleUsage = `
Example Rejection Usage:
\`\`\`
❌
reason: staff availability
name: Ian Henry Atkins
\`\`\`
Example Acceptance Usage:
\`\`\`
✅
name: Ian Henry Atkins
\`\`\`
`;

function acceptTemplate(
	{ name, eventName, date }: {
		name: string;
		eventName: string;
		date: string;
	},
): string {
	return `\
Hi ${name},

This email confirms that WJTB can provide live sound for your event, ${eventName}, on ${date}.

Best,
The WJTB Team
`.trim();
}

function rejectTemplate({ name, eventName, date, reason }: {
	name: string;
	eventName: string;
	date: string;
	reason: string;
}): string {
	return `\
Hi ${name},

Thank you for submitting a live sound request for WJTB! Unfortunately we cannot do your event, ${eventName}, on ${date} due to ${reason}.

Our apologies, 
The WJTB Team
`.trim();
}

export async function emailSender(
	message: typeof bot.transformers.$inferredTypes.message,
) {
	const channel = await bot.rest.getChannel(message.channelId);
	if (
		channel.name != "upcoming-events"
	) return; // wrong channel
	if (message.type != MessageTypes.Reply) return; // not a reply
	if (!message.referencedMessage) return; // referenced message was deleted
	const content = message.content.trim();
	const accepted = content.startsWith("✅");
	const rejected = content.startsWith("❌");
	if (!(accepted || rejected)) return; // not an email sender message
	if (!channel.guildId) return; // channel isnt in a guild
	const roleId = (await bot.rest.getRoles(channel.guildId)).find((role) =>
		role.name == "live-events-email-sender"
	)?.id;
	if (!roleId) {
		bot.logger.error("no email sender role");
		return;
	}
	if (
		!(await bot.rest.getMember(channel.guildId, message.author.id)).roles.find((
			r,
		) => r == roleId)
	) return;
	const fields = parseMessage(content);
	if (!fields["name"]) {
		return await sendErrorReply(message, "name not provided." + exampleUsage);
	}
	if (rejected && !fields["reason"]) {
		return await sendErrorReply(message, "reason not provided." + exampleUsage);
	}
	if (
		!message.referencedMessage.embeds ||
		message.referencedMessage.embeds.length <= 0
	) {
		return await sendErrorReply(
			message,
			"referenced message doesnt have an embed",
		);
	}
	const toEmail =
		/ ?A new live event has been submitted. ?\n ?Someone with the following email (?<email>.*@.*) responded to the survey/im
			.exec(
				message
					.referencedMessage.content,
			)?.groups?.email;
	if (!toEmail) return await sendErrorReply(message, "failed to parse email");

	const embedContent = message.referencedMessage.embeds[0].description;
	if (!embedContent) {
		return await sendErrorReply(
			message,
			"referenced message embed doesn't have a description",
		);
	}

	const liveEvent = parseLiveEvent(embedContent);
	if (!liveEvent) {
		return await sendErrorReply(
			message,
			"failed to parse embed content",
		);
	}

	addEventToCalendar(liveEvent);

	// reply to the email
	const eventDate = format(
		parseDate(liveEvent.start),
		"eeee, MMMM do, yyyy",
	);

	const response = accepted
		? acceptTemplate({
			name: fields.name,
			eventName: liveEvent.name,
			date: eventDate,
		})
		: rejectTemplate({
			name: fields.name,
			eventName: liveEvent.name,
			date: eventDate,
			reason: fields.reason,
		});
	if (!env.EMAIL_USERNAME) {
		return await sendErrorReply(
			message,
			"config error. email username not set.",
		);
	}
	if (!env.EMAIL_PASSWORD) {
		return await sendErrorReply(
			message,
			"config error. email password not set.",
		);
	}

	const transporter = nodemailer.createTransport({
		host: "smtp.gmail.com",
		port: 465,
		secure: true,
		auth: { user: env.EMAIL_USERNAME, pass: env.EMAIL_PASSWORD },
	});
	let success = true;
	await transporter.sendMail({
		from: "wjtb@njit.edu",
		to: toEmail,
		subject: "WJTB Sound Request",
		text: response,
	}).catch((err) => {
		success = false;
		bot.logger.error(err);
		sendErrorReply(
			message,
			"failed to send email",
		);
	});
	if (!success) return;

	return await sendReply(
		message,
		`Email sent ✅\
\`\`\`\
${response}\
\`\`\``,
	);
}
