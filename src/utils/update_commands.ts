import { bot } from "../bot.ts";
import { commands } from "../commands.ts";

export async function updateApplicationCommands(): Promise<void> {
	await bot.helpers.upsertGlobalApplicationCommands(commands.array());
}
