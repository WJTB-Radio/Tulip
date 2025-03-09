import { load } from "@dotenv";

export const env = await load();
const token = env.TOKEN;

if (!token) throw new Error("Missing TOKEN environment variable");

export const configs: Config = {
	token,
};

export interface Config {
	token: string;
}
