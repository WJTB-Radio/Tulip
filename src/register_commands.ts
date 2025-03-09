import "./config.ts";

import { bot } from "./bot.ts";
import importDirectory from "./utils/loader.ts";
import { updateApplicationCommands } from "./utils/update_commands.ts";
import process from "node:process";

bot.logger.info("Loading commands...");
await importDirectory("src/commands");

bot.logger.info("Updating commands...");
await updateApplicationCommands();

bot.logger.info("Done!");

// We need to manually exit as the REST Manager has timeouts that will keep NodeJS alive
process.exit();
