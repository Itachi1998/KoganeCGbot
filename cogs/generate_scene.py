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
        # It's good practice to create the client inside the method 
        # if the cog is long-lived, to handle session expiration.
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

            # Read the streaming body from the Lambda response
            response_body = response['Payload'].read()
            
            # The body is a JSON string, so we parse it into a Python dict
            response_payload = json.loads(response_body)

            # Your Lambda function likely returns a JSON object where the 
            # image data is base64-encoded in a specific key.
            # A common key name is 'body'. If your Lambda uses a different key,
            # replace 'body' with the correct key name.
            if 'body' in response_payload:
                image_data_base64 = response_payload['body']
            else:
                # If you're unsure of the key, you might want to print the payload
                # to inspect its structure.
                print("Error: 'body' key not found in Lambda response. Full payload:", response_payload)
                return

            # Decode the base64 string into bytes
            image_bytes = base64.b64decode(image_data_base64)

            # Write the decoded bytes to the output file
            with open(self.output_file, 'wb') as f:
                f.write(image_bytes)
            
            print(f"Image saved to {self.output_file}")

        except Exception as e:
             print(f"Error calling lambda function or processing its response: {e}")
        
    
async def setup(bot):
    await bot.add_cog(Generate(bot))
