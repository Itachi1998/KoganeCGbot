import boto3, json, base64, os, io

lambda_name = "cullinggame-images"
async def attack_scene(attacker, target, lobby, bot):
        """Invokes lambda function, retrieves the merged image, and sends it to the log channel."""
        client = boto3.client('lambda')
        payload={ 
                
                "bucket_name": lambda_name,
                
                "image1" : lobby.background,
                
                "image2" : attacker.name,
                
                "image3" : target.name,
                "text1" : "Comedian:\n    BE MY WIFI!",
                'text2' : "Domain Expansion:\n   Deadly Sentence"
                
                } 
        try:
            response = await bot.loop.run_in_executor(
                None,
                lambda: client.invoke(
                FunctionName=lambda_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
                )
                )
        
            if 'FunctionError' in response:
                error_payload = json.loads(response['Payload'].read())
                print(f"Lambda function returned an error: {error_payload}")
                return

            response_body = response['Payload'].read()

            # Corrected Parsing Logic:
            response_payload = json.loads(response_body)
            body_string = response_payload.get('body')
            if not body_string:
                print("Error: 'body' key not found in Lambda response.")
                return

            inner_payload = json.loads(body_string)
            image_data_base64 = inner_payload.get('image')

            if not image_data_base64 or not isinstance(image_data_base64, str):
                print(f"Error: Could not extract a valid base64 string from Lambda response. Got: {image_data_base64}")
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
                    file = discord.File(io.BytesIO(image_bytes), filename='merged_image.png')
                    await log_channel.send("Generated Scene:", file=file)
                    print(f"Image successfully sent to channel {log_channel.name}")
                else:
                    print(f"Error: Could not find channel with ID {log_channel_id}")

            except Exception as e:
                print(f"Error during base64 decoding or sending to Discord: {e}")

        except Exception as e:
             print(f"An unexpected error occurred during Lambda invocation: {e}")