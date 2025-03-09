import {
	ApplicationCommandTypes,
	createEmbeds,
	snowflakeToTimestamp,
} from "@discordeno/bot";
import { createCommand } from "../commands.ts";

createCommand({
	name: "pingtulip",
	description: "check tulip's latency",
	type: ApplicationCommandTypes.ChatInput,
	async execute(interaction) {
		const ping = Date.now() - snowflakeToTimestamp(interaction.id);

		const embeds = createEmbeds().setTitle(`The bot ping is ${ping}ms`);

		await interaction.respond({ embeds });
	},
});
