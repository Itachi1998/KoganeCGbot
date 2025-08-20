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
        client = boto3.client('lambda')
        payload = {"bucket_name": self.s3_bucket,
                   "image1_key" : self.img1,
                   "image2_key" : self.img2
                   }
        try:
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
            image_data_base64 = None

            # Attempt to parse the response as JSON.
            try:
                # The response from Lambda invoke is often a JSON payload.
                response_payload = json.loads(response_body)
                
                # Check for a 'body' key, common in API Gateway proxy responses.
                # The body itself might be a JSON string, so we parse it again.
                if 'body' in response_payload:
                    try:
                        image_data_base64 = json.loads(response_payload['body'])
                    except (json.JSONDecodeError, TypeError):
                         # If the body is not a JSON string, use it directly.
                        image_data_base64 = response_payload['body']
                else:
                    # If no 'body', maybe the whole payload is the base64 string.
                    # This is unlikely if it parsed as a dict, but we'll handle it.
                    image_data_base64 = response_payload

            except json.JSONDecodeError:
                # If it's not JSON, assume the whole response body is the base64 string.
                # We decode it to a string first.
                image_data_base64 = response_body.decode('utf-8')

            if not image_data_base64 or not isinstance(image_data_base64, str):
                print(f"Error: Could not extract a valid base64 string from Lambda response. Got: {image_data_base64}")
                return

            try:
                # Remove potential surrounding quotes from a stringified JSON payload
                image_data_base64 = image_data_base64.strip('"')

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
