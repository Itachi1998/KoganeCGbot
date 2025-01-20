import boto3

from botocore.exceptions import ClientError

def get_secret(): 
    
    session = boto3.session.Session()
    secret_name = "arn:aws:secretsmanager:us-east-2:302263061226:secret:prod/KoganeSecrets-x7LtVt" 
    region_name = "us-east-2" 
    # Create a Secrets Manager
    client = session.client(
         service_name ='secretsmanager', 
         region_name = region_name)

    try:
         get_secret_value_response = client.get_secret_value(SecretId =secret_name )
    except ClientError as e:
                 print(e)
                 raise e
                 

    secret = get_secret_value_response['TOKEN']
    return secret 


sec = get_secret()
print(sec)


            