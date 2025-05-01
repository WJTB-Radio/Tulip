import {
	createBot,
	Intents,
	LogDepth,
	type logger as discordenoLogger,
} from "@discordeno/bot";
import { createProxyCache } from "dd-cache-proxy";
import { configs } from "./config.ts";

const rawBot = createBot({
	token: configs.token,
	intents: Intents.Guilds | Intents.MessageContent | Intents.GuildMembers |
		Intents.GuildMessages,
	desiredProperties: {
		interaction: {
			id: true,
			type: true,
			data: true,
			token: true,
			guildId: true,
			member: true,
		},
		guild: {
			id: true,
			name: true,
			roles: true,
			ownerId: true,
		},
		role: {
			id: true,
			guildId: true,
			permissions: true,
		},
		member: {
			id: true,
			roles: true,
			nick: true,
		},
		channel: {
			id: true,
			guildId: true,
		},
		user: {
			id: true,
			username: true,
			globalName: true,
			discriminator: true,
		},
		message: {
			content: true,
			author: true,
			channelId: true,
			referencedMessage: true,
			type: true,
			guildId: true,
			id: true,
			embeds: true,
		},
	},
});

export const bot = createProxyCache(rawBot, {
	desiredProps: {
		guild: ["id", "name", "ownerId", "roles"],
		roles: ["id", "guildId", "permissions"],
	},
	cacheInMemory: {
		guild: true,
		role: true,
		default: false,
	},
}); // By default, bot.logger will use an instance of the logger from @discordeno/bot, this logger supports depth and we need to change it, so we need to say to TS that we know what we are doing with as
(bot.logger as typeof discordenoLogger).setDepth(LogDepth.Full);
