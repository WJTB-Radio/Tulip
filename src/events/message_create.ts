import { bot } from "../bot.ts";
import { emailSender } from "../features/email_sender.ts";
import { liveChatOnMessage } from "../features/live_chat.ts";

bot.events.messageCreate = async (message) => {
	for (const reciever of [emailSender, liveChatOnMessage]) {
		await reciever(message);
	}
};
