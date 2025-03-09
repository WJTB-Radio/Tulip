import { ApplicationCommandTypes } from "@discordeno/bot";
import { createCommand } from "../commands.ts";

createCommand({
	name: "restarticecast",
	description: "restart icecast (if butt wont connect)",
	type: ApplicationCommandTypes.ChatInput,
	async execute(interaction) {
		await interaction.respond({ content: "hello" });
	},
});
