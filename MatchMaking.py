import json
import boto3
import decimal

def lambda_handler(event, context):
    
    db = boto3.resource("dynamodb")
    table = db.Table("Assignment3DB")
    
    if 'body' in event:
        
        getResponse = table.get_item(
            Key={
                'user_id': (json.loads(event['body']))['user_id']
                
            }
        )
        
        itemDetails = getResponse["Item"]
        
        print(event['body'])
        
        # TODO implement
        return {
            'statusCode': 200,
            'body': json.dumps(itemDetails)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('bad id')
    }