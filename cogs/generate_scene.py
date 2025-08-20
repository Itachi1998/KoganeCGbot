import boto3, json, base64, os, io, PIL
from PIL import Image
import discord
from discord.ext import commands

class Generate(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.lambda_name = 'Demo-Pillow-Lambda'
        self.s3_bucket= 'cullinggame-images'
        self.img1 = 'IMG_2120-3.png'
        self.img2 = 'IMG_3530.png'
        self.output_file='merged_image.png'
        self.call_lambda_and_save_image()
    
    def call_lambda_and_save_image(self):
        """Invokes lambda function, retrieves the merged image, and saves it locally."""
        client = boto3.client('lambda')
        payload = {"bucket_name": self.s3_bucket,
                   "image1_key" : self.img1,
                   "image2_key" : self.img2
                   }
        try:
            response = client.invoke(
                FunctionName=self.lambda_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            if 'FunctionError' in response:
                error_payload = json.loads(response['Payload'].read())
                print(f"Lambda function returned an error: {error_payload}")
                return

            response_body = response['Payload'].read()
            
            # --- DEBUGGING STEP 1: Print the raw response from Lambda ---
            # This will show us exactly what the function is sending back.
            print("Raw Lambda response body:", response_body)

            try:
                response_payload = json.loads(response_body)
            except json.JSONDecodeError:
                print("Error: Failed to decode Lambda response as JSON. The response may not be in JSON format.")
                return

            # --- DEBUGGING STEP 2: Print the parsed payload ---
            print("Parsed Lambda response (JSON):", response_payload)

            if 'body' in response_payload:
                image_data_base64 = response_payload['body']
                
                # --- DEBUGGING STEP 3: Print the string we are about to decode ---
                print("Attempting to decode this string:", image_data_base64)
                
                try:
                    # A valid base64 string's length must be a multiple of 4.
                    # This adds the required padding if it's missing.
                    missing_padding = len(image_data_base64) % 4
                    if missing_padding:
                        image_data_base64 += '=' * (4 - missing_padding)
                    
                    image_bytes = base64.b64decode(image_data_base64)
                    
                    with open(self.output_file, 'wb') as f:
                        f.write(image_bytes)
                    
                    print(f"Image successfully decoded and saved to {self.output_file}")

                except Exception as e:
                    print(f"Error during base64 decoding: {e}")
                    print("This usually means the 'body' of the response is not a valid base64 string.")
            else:
                print("Error: 'body' key not found in Lambda response.")

        except Exception as e:
             print(f"An unexpected error occurred: {e}")
        
    
async def setup(bot):
    await bot.add_cog(Generate(bot))
