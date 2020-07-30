import logging
import boto3
import json
from botocore.exceptions import ClientError
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sesv2 = boto3.client('sesv2')

notification_type_recipients_dict = {
    'Bounce': 'bouncedRecipients',
    'Complaint': 'complainedRecipients'
}

def is_registered_suppresion_list(email_address, notification_type):
    response = {}
    try:
        response = sesv2.get_suppressed_destination(EmailAddress=email_address)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotFoundException':
            return False
        else:
            raise e

    if response:
        logger.info('[{}] {} is already registered. response is below\n{}'.format(notification_type,email_address, response))
        return True


def lambda_handler(event, context):
    logging.info('sqs_event:{}'.format(event))
 
    for record in event['Records']:
        sqs_message_body = json.loads(record['body'])
        logging.info('sqs_message_body:{}'.format(sqs_message_body))
        ses_info = json.loads(sqs_message_body['Message'])
        
        logging.info('ses_info:{}'.format(ses_info))
        notification_type = ses_info['notificationType']
        if ses_info['notificationType'] not in ['Bounce', 'Complaint']:
            return {'statusCode': 200, 'body': '[SKIP][{}] is not notification from SES.'.format(notification_type)}
        
        logging.info('debug:{}'.format(ses_info[notification_type.lower()][notification_type_recipients_dict[notification_type]]))
        for recipient in ses_info[notification_type.lower()][notification_type_recipients_dict[notification_type]]:
            logger.info('mail:{}'.format(recipient['emailAddress']))

            if recipient['emailAddress'] == 'bounce@simulator.amazonses.com':
                logger.info('[SKIP][{}] {} is test mail address.'.format(notification_type,recipient['emailAddress']))
                continue
            if is_registered_suppresion_list(recipient['emailAddress'], notification_type):
                continue

            logger.info('[{}] {} is not registered to account level suppresion list. So call put_suppressed_destination'.format(notification_type,recipient['emailAddress']))
            put_suppressed_res = sesv2.put_suppressed_destination(
                EmailAddress=recipient['emailAddress'],
                Reason=notification_type.upper()
            )
            logger.info('[{}] {} is registered to account level suppresion list. response is below\n{}'.format(notification_type,recipient['emailAddress'], put_suppressed_res))
            
    logger.info('got event {}'.format("OK"))
    return {
        'statusCode': 200,
        'body': 'SES suppression-auto-register finished.'
    }

def main():
    context = {}

    args = sys.argv
    if (len(args) == 2):
        aws_profile = args[1]
        session = boto3.Session(profile_name=aws_profile)
        global sesv2
        sesv2 = session.client('sesv2')
        logger.info('Use .aws/credential info. profile name [{}]'.format(aws_profile))

    with open('test_event/ses_suppression_list_auto_register.json') as f:
        event = json.load(f)
    lambda_handler(event, context)

if __name__ == "__main__":
    main()