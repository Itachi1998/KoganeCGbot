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
    
    def call_lambda_and_save_image(lambda_name, bucket_name, image1_key, image2_key, o_filename):
        """Invokes lambda functionm retrieves the merged image, and saves it locally."""
        client = boto3.client('lambda')
        payload = {"bucket_name": bucket_name,
                   "image1_key" : image1_key,
                   "image2_key" : image2_key
                   }
        try:
            response = client.invoke(
                FunctionName=lambda_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            if 'FunctionError' in response:
                    error_payload = json.loads(response['Payload'].read())
                    print(f"Lambda function returned an error: {error_payload}")
                    return
            response_payload=json.loads(response['Payload'].read())
            with open(o_filename, 'wb') as f:
                f.write(response_payload)
            print(f"Image saved to {o_filename}")
        except Exception as e:
             print(f"Error calling lambda function: {e}")
        
        call_lambda_and_save_image(lambda_name=self.lambda_name, bucket_name=self.s3_bucket, image1_key=self.img1, image2_key=self.img2, o_filename=self.output_file)
    
async def setup(bot):
    await bot.add_cog(Generate(bot))
