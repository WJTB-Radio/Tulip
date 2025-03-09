import "./config.ts";

import { bot } from "./bot.ts";
import importDirectory from "./utils/loader.ts";
import { liveChatStartup } from "./features/live_chat.ts";
import { startupCalendar } from "./features/event_calendar.ts";

bot.logger.info("Starting bot...");

bot.logger.info("Loading commands...");
await importDirectory("src/commands");

bot.logger.info("Loading events...");
await importDirectory("src/events");

liveChatStartup();
startupCalendar();

await bot.start();
