# import boto3, json, base64, os, io
import discord
from discord.ext import commands

class Generate(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.lambda_name = 'Demo-Pillow-Lambda'
        self.s3_bucket= 'cullinggame-images'
        self.img1 = 'IMG_2120-3.png'
        self.img2 = 'IMG_3530.png'
        self.img3 = "color-facade-factory-industry-energy-shipping-container-59287-pxhere.com.png"
        
    
#     @commands.command()
#     @commands.is_owner() # Optional: restricts this command to the bot owner
#     async def generate(self, ctx):
#         """Invokes the Lambda function to generate an image and sends it to the log channel."""
#         await ctx.send("Generating image...")
#         await self.call_lambda_and_send_image()

    
        
        
    
async def setup(bot):
    await bot.add_cog(Generate(bot))
