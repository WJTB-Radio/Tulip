import { bot } from "../bot.ts";

bot.events.ready = ({ user, shardId }) => {
	if (shardId === bot.gateway.lastShardId) {
		// All shards are ready
		bot.logger.info(
			`Successfully connected to the gateway as ${user.username}#${user.discriminator}`,
		);
	}
};
