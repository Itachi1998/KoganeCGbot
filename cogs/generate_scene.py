import boto3, json, base64, os, io
import discord
from discord.ext import commands

class Generate(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.lambda_name = 'Demo-Pillow-Lambda'
        self.s3_bucket= 'cullinggame-images'
        self.img1 = 'IMG_2120-3.png'
        self.img2 = 'IMG_3530.png'
    
    @commands.command()
    @commands.is_owner() # Optional: restricts this command to the bot owner
    async def generate(self, ctx):
        """Invokes the Lambda function to generate an image and sends it to the log channel."""
        await ctx.send("Generating image...")
        await self.call_lambda_and_send_image()

    async def call_lambda_and_send_image(self):
        """Invokes lambda function, retrieves the merged image, and sends it to the log channel."""
        # It's better to create the client inside the method for thread safety with async
        # and to allow for updated credentials if the bot runs for a long time.
        client = boto3.client('lambda')
        payload = {"bucket_name": self.s3_bucket,
                   "image1_key" : self.img1,
                   "image2_key" : self.img2
                   }
        try:
            # boto3 calls are blocking, run them in an executor to avoid blocking the bot's event loop
            response = await self.bot.loop.run_in_executor(
                None, 
                lambda: client.invoke(
                    FunctionName=self.lambda_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )
            )
            
            if 'FunctionError' in response:
                error_payload = json.loads(response['Payload'].read())
                print(f"Lambda function returned an error: {error_payload}")
                return

            response_body = response['Payload'].read()

            try:
                response_payload = json.loads(response_body)
            except json.JSONDecodeError:
                print("Error: Failed to decode Lambda response as JSON. The response may not be in JSON format.")
                # If the raw response might be the image, let's try to decode it.
                image_data_base64 = response_body.decode('utf-8')
            else:
                 if 'body' in response_payload:
                    image_data_base64 = response_payload['body']
                 else:
                    print("Error: 'body' key not found in Lambda response.")
                    return
            
            try:
                # Add padding if required
                missing_padding = len(image_data_base64) % 4
                if missing_padding:
                    image_data_base64 += '=' * (4 - missing_padding)
                
                image_bytes = base64.b64decode(image_data_base64)
                
                log_channel_id = os.getenv('LOGCHANNEL')
                if not log_channel_id:
                    print("Error: LOGCHANNEL environment variable not set.")
                    return
                
                log_channel = self.bot.get_channel(int(log_channel_id))

                if log_channel:
                    # Use io.BytesIO to send the raw bytes as a file
                    file = discord.File(io.BytesIO(image_bytes), filename='merged_image.png')
                    await log_channel.send("Generated Scene:", file=file)
                    print(f"Image successfully sent to channel {log_channel.name}")
                else:
                    print(f"Error: Could not find channel with ID {log_channel_id}")

            except Exception as e:
                print(f"Error during base64 decoding or sending to Discord: {e}")

        except Exception as e:
             print(f"An unexpected error occurred during Lambda invocation: {e}")
        
    
async def setup(bot):
    await bot.add_cog(Generate(bot))
