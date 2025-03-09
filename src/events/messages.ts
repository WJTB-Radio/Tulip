import { bot } from "../bot.ts";
import { emailSender } from "../features/email_sender.ts";
import {
	liveChatDeleteMessage,
	liveChatOnMessage,
} from "../features/live_chat.ts";

bot.events.messageCreate = async (message) => {
	for (const reciever of [emailSender, liveChatOnMessage]) {
		await reciever(message);
	}
};

bot.events.messageDelete = async (event) => {
	await liveChatDeleteMessage(event);
};

bot.events.messageDeleteBulk = async (event) => {
	for (const id of event.ids) {
		await liveChatDeleteMessage({ id, channelId: event.channelId });
	}
};
