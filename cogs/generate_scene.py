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
        """Invokes lambda functionm retrieves the merged image, and saves it locally."""
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
            response_payload=json.loads(response['Payload'].read())
            with open(self.output_file, 'wb') as f:
                f.write(response_payload)
            print(f"Image saved to {self.output_file}")
        except Exception as e:
             print(f"Error calling lambda function: {e}")
        
    
async def setup(bot):
    await bot.add_cog(Generate(bot))
