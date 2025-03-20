import discord
from discord.ext import commands
from discord import app_commands


class Lobby_Cog(commands.Cog):
    def __init__(self, bot): 
         self.bot = bot
    

    @discord.app_commands.command(name="create_private_thread", description="Creates a private thread")
    @discord.app_commands.describe(thread_name="The name of the thread")
    async def create_private_thread(self, interaction: discord.Interaction, thread_name: str):
        try:
            thread = await interaction.channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread)
            await interaction.response.send_message(f"Private thread '{thread_name}' created successfully!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I do not have the required permissions to create a private thread.", ephemeral=True)
        except discord.HTTPException as e:
             await interaction.response.send_message(f"Failed to create thread: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ThreadCog(bot))