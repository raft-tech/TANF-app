import json, os
import boto3

OS_ENV = os.environ

def run():
    sys_values = {}    
    sys_values['S3_ENV_VARS'] = json.loads(OS_ENV['VCAP_SERVICES'])['s3']
    sys_values['S3_CREDENTIALS'] = sys_values['S3_ENV_VARS'][0]['credentials']
    sys_values['S3_URI'] = sys_values['S3_CREDENTIALS']['uri']
    sys_values['S3_ACCESS_KEY_ID'] = sys_values['S3_CREDENTIALS']['access_key_id']
    sys_values['S3_SECRET_ACCESS_KEY'] = sys_values['S3_CREDENTIALS']['secret_access_key']
    sys_values['S3_BUCKET'] = sys_values['S3_CREDENTIALS']['bucket']
    sys_values['S3_REGION'] = sys_values['S3_CREDENTIALS']['region']
    sys_values['DATABASE_URI'] = OS_ENV['DATABASE_URL']

    # Set AWS credentials in env, Boto3 uses the env variables for connection
    os.environ["AWS_ACCESS_KEY_ID"] = sys_values['S3_ACCESS_KEY_ID']
    os.environ["AWS_SECRET_ACCESS_KEY"] = sys_values['S3_SECRET_ACCESS_KEY']

    s3 = boto3.resource("s3")
    for bucket in s3.buckets.all():
        print('=================================================')
        print(bucket.name)
        print(bucket.Versioning().status)
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

run()
