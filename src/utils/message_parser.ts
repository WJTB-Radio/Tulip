export function parseMessage(message: string): Record<string, string> {
	return message.split("\n").reduce((acc, line) => {
		const s = line.split(":");
		if (s.length >= 2) {
			acc[s[0]] = s.slice(1).join(":").trim();
		}
		return acc;
	}, {} as Record<string, string>);
}
