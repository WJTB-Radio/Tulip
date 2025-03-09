import { commandOptionsParser, InteractionTypes } from "@discordeno/bot";
import { bot } from "../bot.ts";
import { commands } from "../commands.ts";

bot.events.interactionCreate = async (interaction) => {
	if (
		!interaction.data ||
		interaction.type !== InteractionTypes.ApplicationCommand
	) return;

	const command = commands.get(interaction.data.name);

	if (!command) {
		bot.logger.error(`Command ${interaction.data.name} not found`);
		return;
	}

	const options = commandOptionsParser(interaction);

	try {
		await command.execute(interaction, options);
	} catch (error) {
		bot.logger.error(
			`There was an error running the ${command.name} command.`,
			error,
		);
	}
};
