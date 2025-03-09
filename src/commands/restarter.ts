import { ApplicationCommandTypes } from "@discordeno/bot";
import { createCommand } from "../commands.ts";
import { env } from "../config.ts";

createCommand({
	name: "restarticecast",
	description: "restart icecast (if butt wont connect)",
	type: ApplicationCommandTypes.ChatInput,
	async execute(interaction) {
		const cmd = new Deno.Command(env.RESTART_STREAM_SCRIPT, { args: [] });
		const { stdout } = await cmd.output();
		const output = new TextDecoder().decode(stdout);
		const content = output.trim().endsWith("ok")
			? "Icecast has been restarted. BUTT should reconnect."
			: "Something went wrong, ask your local web person for help.";
		await interaction.respond({ content });
	},
});
