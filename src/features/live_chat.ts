import { bot } from "../bot.ts";
import { env } from "../config.ts";
import { Application, Context, Router } from "@oak/oak";

interface ChatMessage {
	content: string;
	user: string;
}
let messages: ChatMessage[] = [];

type SocketMessage = { type: "full"; messages: ChatMessage[] } | {
	type: "message";
	message: ChatMessage;
};

export async function liveChatOnMessage(
	message: typeof bot.transformers.$inferredTypes.message,
) {
	const channel = await bot.rest.getChannel(message.channelId);
	if (
		channel.name != "upcoming-events" || !message.guildId
	) return; // wrong channel
	const member = await bot.rest.getMember(message.guildId, message.author.id);
	if (messages.length > 100) {
		messages.shift();
	}
	const chatMessage = {
		content: message.content,
		user: member.nick ?? message.author.username,
	};
	messages.push(chatMessage);
	for (const socket of sockets) {
		socket.send(
			JSON.stringify(
				{ type: "message", message: chatMessage } as SocketMessage,
			),
		);
	}
}

export async function liveChatStartup() {
	const guildId = env.GUILD_ID;
	if (!guildId) {
		bot.logger.error("config error: GUILD_ID not set");
		return;
	}
	const channel = (await bot.rest.getChannels(guildId)).find((channel) =>
		channel.name == "live-show-chat"
	);
	if (!channel) return; // no live show chat
	messages = [];
	const message_list = await bot.rest.getMessages(channel.id, { limit: 100 });
	for (const message of message_list) {
		if (!message.content) continue;
		const member = await bot.rest.getMember(guildId, message.author.id);
		messages.push({
			content: message.content,
			user: member.nick ?? message.author.username,
		});
	}
	const router = new Router();
	router.get("/", getRecentMessages);
	const app = new Application();
	app.use(router.routes());
	app.use(router.allowedMethods());
	app.listen({ port: 8010 });
}

const sockets: Set<WebSocket> = new Set();

export function getRecentMessages(
	ctx: Context,
) {
	if (!ctx.isUpgradable) {
		ctx.response.body = "must upgrade to websocket";
		ctx.response.status = 400;
		return;
	}
	const ws = ctx.upgrade();
	ws.onopen = () => {
		ws.send(JSON.stringify({ type: "full", messages } as SocketMessage));
		sockets.add(ws);
	};
	ws.onclose = () => {
		sockets.delete(ws);
	};
}
