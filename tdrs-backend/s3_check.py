import json, os
import boto3
import logging

OS_ENV = os.environ

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
os.environ["AWS_DEFAULT_REGION"] = sys_values['S3_REGION']

logger.info("=============LOGER CHECK===============")

s3_client = boto3.client('s3', region_name=sys_values['S3_REGION'])
versioning = s3_client.get_bucket_versioning(Bucket=sys_values['S3_BUCKET'])
logger.info(f"Version: {versioning}")
