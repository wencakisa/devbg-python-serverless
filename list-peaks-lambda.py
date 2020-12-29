import json
import boto3

aws_region = 'eu-central-1'

s3 = boto3.client('s3', aws_region)
ssm = boto3.client('ssm', aws_region)

bucket_name = ssm.get_parameter(Name='peaks-bucket-name')['Parameter']['Value']
file_name = ssm.get_parameter(Name='peaks-file-name')['Parameter']['Value']

def lambda_handler(event, context):
    query_params = event.get('queryStringParameters')

    expression = 'select * from s3object'

    if query_params and 'mountain' in query_params:
        expression = "select * from s3object[*].peaks[*] as peak where peak.mountain = '" + query_params['mountain'] + "'"

    response = s3.select_object_content(
        Bucket=bucket_name,
        Key=file_name,
        Expression=expression,
        ExpressionType='SQL',
        InputSerialization={'JSON': {'Type': 'Document'}},
        OutputSerialization={'JSON': {}}
    )

    records = {}

    for event in response['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode()

    return {
        'statusCode': 200,
        'body': json.dumps(records)
    }
