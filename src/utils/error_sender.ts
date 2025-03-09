import { DiscordMessageReferenceType } from "@discordeno/types";
import { bot } from "../bot.ts";

export async function sendReply(
	to: typeof bot.transformers.$inferredTypes.message,
	message: string,
) {
	return await bot.rest.sendMessage(to.channelId, {
		messageReference: {
			type: DiscordMessageReferenceType.Default,
			channelId: to.channelId,
			guildId: to.guildId,
			messageId: to.id,
			failIfNotExists: true,
		},
		content: message,
	});
}

export async function sendErrorReply(
	to: typeof bot.transformers.$inferredTypes.message,
	errorMessage: string,
) {
	return await sendReply(to, `❌ error:\n${errorMessage}`);
}
