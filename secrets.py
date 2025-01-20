import boto3

from botocore.exceptions import ClientError

def get_secret(): 
    
    session = boto3.session.Session()
    secret_name = "prod /KoganeSecrets" 
    region_name = "us-east-2" 
    # Create a Secrets Manager
    client = session.client(
         service_name ='secretsmanager', 
         region_name = region_name)

    try:
         get_secret_value_response = client.get_secret_value( 
            SecretId =secret_name 
    except ClientError as e:
                 raise e
                 

    secret = get_secret_value_response['TOKEN']
    print(secret)
            