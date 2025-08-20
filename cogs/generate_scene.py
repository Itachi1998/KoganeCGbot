import boto3, json, base64, os, io
from PIL import Image


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
    


if __name__ == '__main__':
    lambda_name = 'Demo-Pillow-Lambda'
    s3_bucket= 'cullinggame-images'
    img1 = 'IMG_2120-3.png'
    img2 = 'IMG_3530.png'
    output_file='merged_image.png'

    call_lambda_and_save_image(lambda_name=lambda_name, bucket_name=s3_bucket, image1_key=img1, image2_key=img2, o_filename=output_file)
    