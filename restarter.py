import subprocess
import discord
import util

def add_commands(tree):
	@tree.command(name="restartstream", description="Run this command to restart the stream if butt wont connect.", guild=discord.Object(id=util.GUILD_ID))
	async def restartstream(context):
		if(not await util.check_admin(context)):
			return
		subprocess_result = subprocess.run(["./restart_stream.sh"], capture_output=True)
		result = subprocess_result.stdout.decode("utf-8").strip()
		stderr = subprocess_result.stderr.decode("utf-8").strip()
		print("restarting stream")
		print(f"stdout:\n{result}")
		print(f"stderr:\n{stderr}")
		message = "The stream has been restarted. BUTT should reconnect." if result.endswith("ok") else "Something went wrong, ask your local web person for help."
		await context.response.send_message(message)
